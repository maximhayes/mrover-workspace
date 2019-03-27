/* Searches.cpp */

#include "avoidances.hpp"
#include "utilities.hpp"
#include "stateMachine.hpp"

#include <iostream>
#include <cmath>
#include <stack>

/*************************************************************************/
/* Avoidance Factory */
/*************************************************************************/
// Avoidance Factory to allow for creation of obstacle avoidance objects. 
// Allows for easy change from obstacle avoidance algorithm to another
Avoidance* AvoidFactory( StateMachine* stateMachine, AvoidanceType type )
{
    Avoidance* avoid = nullptr;
    switch (type)
    {
        case AvoidanceType::ORIGINAL:
            avoid = new Original( stateMachine );
            break;

        case AvoidanceType::UNKNOWN:
            std::cerr << "Unkown Search Type. Defaulting to original\n";
            avoid = new Original( stateMachine );
            break;
    }
    return avoid;
}

/*************************************************************************/
/* Original Obstacle Avoidance Algorithm 
   When an obstacle is detected, the rover will drive around whichever way 
   CV decides is the fastest. If the tennisball is detected, the heirarchy has 
   two cases in which the rover will begin to turn to tennis ball:
        1. the difference in distance (tennis ball is closer than obs)
        2. Turning around obs is same direction to turn to tennis ball */
/*************************************************************************/
Original::~Original() {}

/*****************************************************/
/* Helpers */
/*****************************************************/

// Executes the logic for turning around an obstacle. 
// If the rover is turned off, it proceeds to Off. 
// If the tennis ball is detected, the rover proceeds to it. 
// If the obstacle is no longer detcted, proceed to drive around the obstacle. 
// Else continue turning around the obstacle.
// ASSUMPTION: We assume that the obstacle is straight ahead of us,
//             therefore we produce an underestimate for how close the waypoint is to the
//             obstacle. This relies on using a path width no larger than what we can
//             confidentally see to the side.
//          
//             There is no rock that is more than 8 meters in diameter
NavState Original::executeTurnAroundObs( Rover * mPhoebe, const rapidjson::Document& mRoverConfig )
{
    
    double cvThresh = mRoverConfig[ "cvThresh" ].GetDouble();

    //if we see the ball and are in a search state, only go to turn to ball if turning 
    //   same direction for obstcle
    if( mPhoebe->roverStatus().currentState() == NavState::SearchTurnAroundObs && 
        mPhoebe->roverStatus().tennisBall().found &&  
      ( cvThresh > mPhoebe->roverStatus().tennisBall().distance - 2 or  //TODO Replace cvThresh with dist to obs
      ( mPhoebe->roverStatus().tennisBall().bearing < 0 && mPhoebe->roverStatus().obstacle().bearing < 0 ) or
      ( mPhoebe->roverStatus().tennisBall().bearing > 0 && mPhoebe->roverStatus().obstacle().bearing > 0 ) ) ) 
    {
        return NavState::TurnToBall;
    }

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

// Executes the logic for driving around an obstacle. 
// If the rover is turned off, proceed to Off. 
// If another obstacle is detected, proceed to go around it. 
// If the rover finished going around the obstacle, it proceeds to 
//      turn to the Waypoint that was being driven to when the
//      obstacle was spotted. 
// Else, continue driving around the obstacle.
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

// Creates the odometry point used to drive around an obstacle
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
    
    std::cout << distance << std::endl;
    std::cout << avoidancePoint.latitude_deg << " " << avoidancePoint.latitude_min << std::endl;
    std::cout << avoidancePoint.longitude_deg << " " << avoidancePoint.longitude_min << std::endl;

    return avoidancePoint;
}
