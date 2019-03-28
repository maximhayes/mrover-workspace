#ifndef SEARCHES_HPP
#define SEARCHES_HPP

#include "searcher.hpp"

enum class SearchType
{
    SPIRALOUT,
    LAWNMOWER,
    SPIRALIN,
    UNKNOWN
};

Searcher* SearchFactory( StateMachine* stateMachine, SearchType type );

/*************************************************************************/
/* SpiralOut Search */
/*************************************************************************/
class SpiralOut : public Searcher 
{
public:
    SpiralOut( StateMachine* stateMachine_ ) 
    : Searcher(stateMachine_) {}

    ~SpiralOut();

    void initializeSearch( Rover* mPhoebe, const rapidjson::Document& mRoverConfig, const double pathWidth );
    
};

/*************************************************************************/
/* SpiralIn Search */
/*************************************************************************/
class SpiralIn : public Searcher 
{
public:
    SpiralIn( StateMachine* stateMachine_ ) 
    : Searcher(stateMachine_) {}

    ~SpiralIn();

    void initializeSearch( Rover* mPhoebe, const rapidjson::Document& mRoverConfig, const double pathWidth );
    
};

/*************************************************************************/
/* LawnMower Search */
/*************************************************************************/
class LawnMower : public Searcher 
{
public:
    LawnMower( StateMachine* stateMachine_ ) 
    : Searcher(stateMachine_) {}

    ~LawnMower();

    void initializeSearch( Rover* mPhoebe, const rapidjson::Document& mRoverConfig, const double pathWidth );

};

#endif //SEARCHES_HPP

/*************************************************************************/
/* TODO */
/*************************************************************************/

