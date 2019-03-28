#include "stateMachine.hpp"

#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <cmath>
#include <cstdlib>

#include "rover_msgs/NavStatus.hpp"
#include "utilities.hpp"
#include "searches.hpp"
#include "avoidances.hpp"

// Constructs a StateMachine object with the input lcm object.
// Reads the configuartion file and constructs a Rover objet with this
// and the lcmObject. Sets mStateChanged to true so that on the first
// iteration of run the rover is updated.
StateMachine::StateMachine( lcm::LCM& lcmObject )
    : mPhoebe( nullptr )
    , mLcmObject( lcmObject )
    , mTotalWaypoints( 0 )
    , mCompletedWaypoints( 0 )
    , mMissedWaypoints( 0 )
    , mStateChanged( true )
{
    ifstream configFile;
    string configPath = getenv("MROVER_CONFIG");
    configPath += "/config_nav/config.json";
    configFile.open( configPath );
    string config = "";
    string setting;
    while( configFile >> setting )
    {
        config += setting;
    }
    configFile.close();
    mRoverConfig.Parse( config.c_str() );
    mPhoebe = new Rover( mRoverConfig, lcmObject );
    mSearcher = SearchFactory( this, SearchType::SPIRALOUT );
    mObstacle = AvoidFactory( this, AvoidanceType::ORIGINAL );
} // StateMachine()

// Destructs the StateMachine object. Deallocates memory for the Rover
// object.
StateMachine::~StateMachine( )
{
    delete mPhoebe;
}

// Function to allow external objects to update completed points
void StateMachine::updateCompletedPoints( )
{
    mCompletedWaypoints += 1;
}

// Allows external objects to change obstacle angle
void StateMachine::updateObstacleAngle( double bearing ) 
{
    mObstacle->updateObstacleAngle( bearing );
}

// Gives external objects access to search point
Odometry StateMachine::frontSearchPoint( )
{
    return mSearcher->frontSearchPoint();
}

// Gives external objects ability to remove search point
void StateMachine::popSearchPoint()
{
    mSearcher->popSearchPoint();
}

// Allows state machine to change search type
void StateMachine::setSearcher( SearchType type )
{
    assert( mSearcher );
    delete mSearcher;
    mSearcher = SearchFactory( this, type );
}

// Runs the state machine through one iteration. The state machine will
// run if the state has changed or if the rover's status has changed.
// Will call the corresponding function based on the current state.
void StateMachine::run()
{
    if( mStateChanged || mPhoebe->updateRover( mNewRoverStatus ) )
    {
        // todo print state, add to publish nav state
        publishNavState();
        mStateChanged = false;
        NavState nextState = NavState::Unknown;

        if( !mPhoebe->roverStatus().autonState().is_auton )
        {
            nextState = NavState::Off;
            clear( mPhoebe->roverStatus().path() );
            if( nextState != mPhoebe->roverStatus().currentState() )
            {
                mPhoebe->roverStatus().currentState() = nextState;
                mStateChanged = true;
            }
            return;
        }

        switch( mPhoebe->roverStatus().currentState() )
        {
            case NavState::Off:
            {
                nextState = executeOff();
                break;
            }

            case NavState::Done:
            {
                nextState = executeDone();
                break;
            }

            case NavState::Turn:
            {
                nextState = executeTurn();
                break;
            }

            case NavState::Drive:
            {
                nextState = executeDrive();
                break;
            }

            case NavState::SearchFaceNorth:
            case NavState::SearchFace120:
            case NavState::SearchFace240:
            case NavState::SearchFace360:
            case NavState::SearchTurn:
            case NavState::SearchDrive:
            case NavState::TurnToBall:
            case NavState::DriveToBall:
            {
                nextState = mSearcher->run( mPhoebe, mRoverConfig );
                break;
            }

            case NavState::TurnAroundObs:
            case NavState::SearchTurnAroundObs:
            case NavState::DriveAroundObs:
            case NavState::SearchDriveAroundObs:
            {
                nextState = mObstacle->run( mPhoebe, mRoverConfig ); //executeDriveAroundObs();
                break;
            }

            case NavState::ChangeSearchAlg:
            {
                static int searchFails = 0;
                static double nPathWidth = mRoverConfig["pathWidth"].GetDouble();

                switch( mRoverConfig[ "searchOrder" ][ searchFails % mRoverConfig[ "searchOrderSize" ].GetInt() ].GetInt() )
                {
                    case 0:
                    {
                        setSearcher(SearchType::SPIRALOUT);
                        break;
                    }
                    case 1:
                    {
                        setSearcher(SearchType::LAWNMOWER);
                        break;
                    }
                    case 2:
                    {
                        setSearcher(SearchType::SPIRALIN);
                        break;
                    }
                    default:
                    {
                        setSearcher(SearchType::SPIRALOUT);
                        break;
                    }
                }
                mSearcher->initializeSearch( mPhoebe, mRoverConfig, nPathWidth );
                if( searchFails % 2 == 1 && nPathWidth > 0.5 )
                {
                    nPathWidth *= 0.5;
                }
                searchFails += 1;
                nextState = NavState::SearchTurn;
                break;
            }

            case NavState::Unknown:
            {
                cout << "Entered unknown state.\n";
                exit(1);
            }
        } // switch

        if( nextState != mPhoebe->roverStatus().currentState() )
        {
            mStateChanged = true;
            mPhoebe->roverStatus().currentState() = nextState;
            mPhoebe->distancePid().reset();
            mPhoebe->bearingPid().reset();
        }
    } // if
} // run()

// Updates the auton state (on/off) of the rover's status.
void StateMachine::updateRoverStatus( AutonState autonState )
{
    mNewRoverStatus.autonState() = autonState;
} // updateRoverStatus( AutonState )

// Updates the course of the rover's status if it has changed.
void StateMachine::updateRoverStatus( Course course )
{
    if( mNewRoverStatus.course().hash != course.hash )
    {
        mNewRoverStatus.course() = course;
    }
} // updateRoverStatus( Course )

// Updates the obstacle information of the rover's status.
void StateMachine::updateRoverStatus( Obstacle obstacle )
{
    mNewRoverStatus.obstacle() = obstacle;
} // updateRoverStatus( Obstacle )

// Updates the odometry information of the rover's status.
void StateMachine::updateRoverStatus( Odometry odometry )
{
    mNewRoverStatus.odometry() = odometry;
} // updateRoverStatus( Odometry )

// Updates the tennis ball information of the rover's status.
void StateMachine::updateRoverStatus( TennisBall tennisBall )
{
    mNewRoverStatus.tennisBall() = tennisBall;
} // updateRoverStatus( TennisBall )

// Publishes the current navigation state to the nav status lcm channel.
void StateMachine::publishNavState() const
{
    NavStatus navStatus;
    navStatus.nav_state = static_cast<int8_t>( mPhoebe->roverStatus().currentState() );
    navStatus.completed_wps = mCompletedWaypoints;
    navStatus.missed_wps = mMissedWaypoints;
    navStatus.total_wps = mTotalWaypoints;
    const string& navStatusChannel = mRoverConfig[ "navStatusChannel" ].GetString();
    mLcmObject.publish( navStatusChannel, &navStatus );
} // publishNavState()

// Executes the logic for off. If the rover is turned on, it updates
// the roverStatus. If the course is empty, the rover is done  with
// the course otherwise it will turn to the first waypoing. Else the
// rover is still off.
NavState StateMachine::executeOff()
{
    if( mPhoebe->roverStatus().autonState().is_auton )
    {
        mCompletedWaypoints = 0;
        mMissedWaypoints = 0;
        mTotalWaypoints = mPhoebe->roverStatus().course().num_waypoints;

        if( !mTotalWaypoints )
        {
            return NavState::Done;
        }
        return NavState::Turn;
    }
    return NavState::Off;
} // executeOff()

// Executes the logic for the done state. Stops and turns off the
// rover.
NavState StateMachine::executeDone()
{
    mPhoebe->stop();
    return NavState::Done;
} // executeDone()

// Executes the logic for the turning. If the rover is turned off, it
// proceeds to Off. If the rover finishes turning, it drives to the
// next Waypoint. Else the rover keeps turning to the Waypoint.
NavState StateMachine::executeTurn()
{
    if( mPhoebe->roverStatus().path().empty() )
    {
        return NavState::Done;
    }

    Odometry& nextPoint = mPhoebe->roverStatus().path().front().odom;
    if( mPhoebe->turn( nextPoint ) )
    {
        return NavState::Drive;
    }
    return NavState::Turn;
} // executeTurn()

// Executes the logic for driving. 
// If the rover is turned off, it proceeds to Off. 
// If the rover finishes driving, it either starts searching for a tennis ball 
//   (dependent the search parameter of the Waypoint) 
//    or it turns to the next Waypoint. 
// If the rover detects an obstacle, 
//     if rover can get to waypoint without avoiding obstacle, continue 
//     else rover goes to turn around obstacle. 
// Else the rover keeps driving to the next Waypoint.
NavState StateMachine::executeDrive()
{
    const Waypoint& nextWaypoint = mPhoebe->roverStatus().path().front();    
    double cvThresh = mRoverConfig[ "cvThresh" ].GetDouble();
    double distance = estimateNoneuclid( mPhoebe->roverStatus().odometry(), nextWaypoint.odom );

    if( mPhoebe->roverStatus().obstacle().detected and
        ( cvThresh < distance - 2 ) )
    {
        mObstacle->updateObstacleAngle( mPhoebe->roverStatus().obstacle().bearing );
        return NavState::TurnAroundObs;
    }

    
    DriveStatus driveStatus = mPhoebe->drive( nextWaypoint.odom );
    if( driveStatus == DriveStatus::Arrived )
    {
        if( nextWaypoint.search )
        {
            return NavState::SearchFaceNorth;
        }
        mPhoebe->roverStatus().path().pop();
        ++mCompletedWaypoints;
        return NavState::Turn;
    }
    if( driveStatus == DriveStatus::OnCourse )
    {
        return NavState::Drive;
    }
    // if driveStatus == DriveStatus::OffCourse
    return NavState::Turn;
} // executeDrive()

// thresholds based on state? waypoint vs ball
// set distance to go around obstacles?
// set threshold for when to skip a point?


// TODOS:
// [turn to ball | drive to ball] if ball lost, restart search a better way??
// [drive to ball] obstacle and ball
// all of code, what to do in cases of both ball and obstacle
// Make it so that there are not so many Update functions. Make functions public? 
    // maybe make variables themselves public?
// [drive] Turn cvThresh into actual distance to rock
