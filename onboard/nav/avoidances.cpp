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


