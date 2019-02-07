#ifndef AVOIDANCE_HPP
#define AVOIDANCE_HPP

#include "avoider.hpp"

enum class AvoidanceType
{
    ORIGINAL,
    TURNBACK,
    UNKNOWN
};

Avoidance* AvoidFactory( StateMachine* stateMachine, AvoidanceType type );

/*************************************************************************/
/* Default Avoidance */
/*************************************************************************/
class Original : public Avoidance 
{
public:
    Original( StateMachine* stateMachine_ ) 
    : Avoidance(stateMachine_) {}

    Odometry createAvoidancePoint( Rover * mPhoebe, const double distance );

    NavState executeTurnAroundObs( Rover* mPhoebe, const rapidjson::Document& mRoverConfig );

    NavState executeDriveAroundObs( Rover* mPhoebe );

    ~Original();
    
};

#endif //AVOIDANCE_HPP


/*************************************************************************/
/* TODO */
/*************************************************************************/
