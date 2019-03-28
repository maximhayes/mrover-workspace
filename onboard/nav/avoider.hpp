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
    : stateMachine(stateMachine_),
    mJustDetectedObstacle(false) {}

    virtual ~Avoidance() {}

    void updateObstacleAngle( double bearing );

    NavState run( Rover * mPhoebe, const rapidjson::Document& mRoverConfig );

    virtual Odometry createAvoidancePoint( Rover * mPhoebe, const double distance ) = 0;

    virtual NavState executeTurnAroundObs( Rover* mPhoebe, const rapidjson::Document& mRoverConfig ) = 0;

    virtual NavState executeDriveAroundObs( Rover* mPhoebe ) = 0;



protected:  // TODO
    /*************************************************************************/
    /* Protected Member Variables */
    /*************************************************************************/
    StateMachine* stateMachine;

    // Odometry point used when avoiding obstacles.
    Odometry mObstacleAvoidancePoint;

    // Initial angle to go around obstacle upon detection.
    double mOriginalObstacleAngle;

    // Switch to check if last action was dealing with an obstacle (trying to turn around it)
    bool mJustDetectedObstacle;

    // Last obstacle angle for consecutive obstacle detections
    double mLastObstacleAngle;

};

#endif //OBSTACLE_HPP

/*************************************************************************/
/* TODO */
/*************************************************************************/