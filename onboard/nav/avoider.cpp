#include "avoider.hpp"
#include "avoidances.hpp"
#include "utilities.hpp"
#include "stateMachine.hpp"

#include <cmath>
#include <iostream>

// Allows outside objects to access obstacle angle
void Avoidance::updateObstacleAngle( double bearing ) 
{
    mOriginalObstacleAngle = bearing;
}

/*****************************************************/
/* Avoidance Run Fuction */
/*****************************************************/
// Runs the state machine through one iteration. The state machine will
// run when the rover is in an obstacle avoidance state (called by StateMachine).
// Will call the corresponding function based on the current state.
NavState Avoidance::run( Rover * mPhoebe, const rapidjson::Document& mRoverConfig )
{
    switch ( mPhoebe->roverStatus().currentState() )
    {
        case NavState::TurnAroundObs:
        case NavState::SearchTurnAroundObs:
        {
            return executeTurnAroundObs( mPhoebe, mRoverConfig );
        }

        case NavState::DriveAroundObs:
        case NavState::SearchDriveAroundObs:
        {
            return executeDriveAroundObs( mPhoebe );
        }

        default:
        {
            return NavState::Unknown;
        }
    } // switch
}