/* Searches.cpp */

#include "avoidances.hpp"
#include "utilities.hpp"
#include "stateMachine.hpp"

#include <iostream>
#include <cmath>
#include <stack>

/*************************************************************************/
/* Searcher Factory */
/*************************************************************************/
Avoidance* AvoidFactory( StateMachine* stateMachine, AvoidanceType type )  //TODO
{
    Avoidance* avoid = nullptr;
    switch (type)
    {
        case AvoidanceType::ORIGINAL:
            avoid = new Original( stateMachine );
            break;

        case AvoidanceType::UNKNOWN:
            std::cerr << "Unkown Search Type. Defaulting to Spiral\n";
            avoid = new Original( stateMachine );
            break;
    }
    return avoid;
}

/*************************************************************************/
/* Spiral Search */
/*************************************************************************/
Original::~Original() {}

/*****************************************************/
/* Helpers */
/*****************************************************/

// Creates the odometry point to use to drive around in obstacle
// avoidance.
Odometry Original::createAvoidancePoint( Rover * mPhoebe, const double distance )
{
    Odometry avoidancePoint = mPhoebe->roverStatus().odometry();
    double totalLatitudeMinutes = avoidancePoint.latitude_min +
        cos( degreeToRadian( avoidancePoint.bearing_deg ) ) * distance * LAT_METER_IN_MINUTES;
    double totalLongitudeMinutes = avoidancePoint.longitude_min +
        sin( degreeToRadian( avoidancePoint.bearing_deg ) ) * distance * mPhoebe->longMeterInMinutes();
    avoidancePoint.latitude_deg += totalLatitudeMinutes / 60;
    avoidancePoint.latitude_min = ( totalLatitudeMinutes - ( ( (int) totalLatitudeMinutes) / 60 ) * 60 );
    avoidancePoint.longitude_deg += totalLongitudeMinutes / 60;
    avoidancePoint.longitude_min = ( totalLongitudeMinutes - ( ( (int) totalLongitudeMinutes) / 60 ) * 60 );
    return avoidancePoint;
}

// Executes the logic for turning around an obstacle. If the rover is
// turned off, it proceeds to Off. If the tennis ball is detected, the
// rover proceeds to it. If the Waypopint and obstacle are in similar
// locations, assume that we would have seen the ball and move on. If
// the obstacle is no longer detcted, proceed to drive around the
// obstacle. Else continue turning around the obstacle.
// ASSUMPTION: To avoid an infinite loop, we assume that the obstacle is straight ahead of us,
//             therefore we produce an underestimate for how close the waypoint is to the
//             obstacle. This relies on using a path width no larger than what we can
//             confidentally see to the side.
NavState Original::executeTurnAroundObs( Rover * mPhoebe, const rapidjson::Document& mRoverConfig )
{
    
    double cvThresh = mRoverConfig[ "cvThresh" ].GetDouble();

    if( mPhoebe->roverStatus().tennisBall().found && 
        mPhoebe->roverStatus().tennisBall().distance - 2 - cvThresh < 0)
    {
        return NavState::TurnToBall;
    }

    // if( ( mPhoebe->roverStatus().currentState() == NavState::TurnAroundObs ) &&
    //     ( estimateNoneuclid( mPhoebe->roverStatus().path().front().odom,
    //                          mPhoebe->roverStatus().odometry() ) < 2 * cvThresh ) )
    // {
    //     mPhoebe->roverStatus().path().pop();
    //     stateMachine->updateMissedWaypoints( ); // mMissedWaypoints += 1;
    //     return NavState::Turn;
    // }
    // if( ( mPhoebe->roverStatus().currentState() == NavState::SearchTurnAroundObs ) &&
    //     ( estimateNoneuclid( stateMachine->frontSearchPoint(), mPhoebe->roverStatus().odometry() )
    //       < 2 * cvThresh ) )
    // {
    //     stateMachine->popSearchPoint();
    //     return NavState::SearchTurn;
    // }

    if( !mPhoebe->roverStatus().obstacle().detected )
    {        
        double distanceAroundObs = cvThresh / cos( fabs( degreeToRadian( mOriginalObstacleAngle ) ) );
        mObstacleAvoidancePoint = createAvoidancePoint( mPhoebe, distanceAroundObs ) ;
        if( mPhoebe->roverStatus().currentState() == NavState::TurnAroundObs )
        {
            return NavState::DriveAroundObs;
        }
        return NavState::SearchDriveAroundObs;
    }
    
    double desiredBearing = mod( mPhoebe->roverStatus().odometry().bearing_deg
                           + mPhoebe->roverStatus().obstacle().bearing, 360 );

    mPhoebe->turn( desiredBearing );
    return mPhoebe->roverStatus().currentState();
} // executeTurnAroundObs()

// Executes the logic for driving around an obstacle. If the rover is
// turned off, proceed to Off. If another obstacle is detected, proceed
// to go around it. If the rover finished going around the obstacle, it
// proceeds to turning to the Waypoint that was being driven to when the
// obstacle was spotted. Else, continue driving around the obstacle.
// TODO: fix the case about when the obstacle gets off course.
NavState Original::executeDriveAroundObs( Rover * mPhoebe )
{
    if( mPhoebe->roverStatus().obstacle().detected )
    {
        mOriginalObstacleAngle = mPhoebe->roverStatus().obstacle().bearing;
        if( mPhoebe->roverStatus().currentState() == NavState::DriveAroundObs )
        {
            return NavState::TurnAroundObs;
        }
        return NavState::SearchTurnAroundObs;
    }

    DriveStatus driveStatus = mPhoebe->drive( mObstacleAvoidancePoint );
    if( driveStatus == DriveStatus::Arrived )
    {
        if( mPhoebe->roverStatus().currentState() == NavState::DriveAroundObs )
        {
            return NavState::Turn;
        }
        return NavState::SearchTurn;
    }
    if( driveStatus == DriveStatus::OnCourse )
    {
        return mPhoebe->roverStatus().currentState();
    }
    if( mPhoebe->roverStatus().currentState() == NavState::DriveAroundObs )
    {
        return NavState::TurnAroundObs;
    }
    return NavState::SearchTurnAroundObs;
} // executeDriveAroundObs()


