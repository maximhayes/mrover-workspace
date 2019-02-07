#ifndef OBSTACLE_HPP
#define OBSTACLE_HPP

#include "rover.hpp"

class StateMachine;

class Avoidance {
public:
    /*************************************************************************/
    /* Public Member Functions */
    /*************************************************************************/
    Avoidance(StateMachine* stateMachine_)
    : stateMachine(stateMachine_) {}

    virtual ~Avoidance() {}

    void updateObstacleAngle( double bearing );

    NavState run( Rover * mPhoebe, const rapidjson::Document& mRoverConfig );

    virtual Odometry createAvoidancePoint( Rover * mPhoebe, const double distance ) = 0;

private:
    /*************************************************************************/
    /* Private Member Functions */
    /*************************************************************************/
    NavState executeTurnAroundObs( Rover* mPhoebe, const rapidjson::Document& mRoverConfig );

    NavState executeDriveAroundObs( Rover* mPhoebe );

protected:  // TODO
    /*************************************************************************/
    /* Protected Member Variables */
    /*************************************************************************/
    StateMachine* stateMachine;

    // Odometry point used when avoiding obstacles.
    Odometry mObstacleAvoidancePoint;

    // Initial angle to go around obstacle upon detection.
    double mOriginalObstacleAngle;

};

#endif //OBSTACLE_HPP

/*************************************************************************/
/* TODO */
/*************************************************************************/
