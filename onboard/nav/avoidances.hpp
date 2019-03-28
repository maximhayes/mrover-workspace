#ifndef AVOIDANCE_HPP
#define AVOIDANCE_HPP

#include "avoider.hpp"

// This class is the representation of different avoidance algorithms
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

    NavState executeTurnAroundObs( Rover* mPhoebe, const rapidjson::Document& mRoverConfig );

    NavState executeDriveAroundObs( Rover* mPhoebe );

    Odometry createAvoidancePoint( Rover * mPhoebe, const double distance );

    ~Original();
    
};

#endif //AVOIDANCE_HPP


/*************************************************************************/
/* TODO */
/*************************************************************************/