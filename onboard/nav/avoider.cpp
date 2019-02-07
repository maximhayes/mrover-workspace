#include "avoider.hpp"
#include "avoidances.hpp"
#include "utilities.hpp"
#include "stateMachine.hpp"

#include <cmath>
#include <iostream>

void Avoidance::updateObstacleAngle( double bearing ) 
{
    mOriginalObstacleAngle = bearing;
    return;
}

/*****************************************************/
/* Avoidance Run Fuction */
/*****************************************************/
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

/*****************************************************/
/* Helpers */
/*****************************************************/

