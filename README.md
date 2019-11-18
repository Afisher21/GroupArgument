# GroupArgument
This is most definitely *not* a free open-sourced program that allows one to play a version of the t.v. show hosted by Steve Harvey (Family Fued) for free at home

# TODO ( No particular order of importance  / implementation)
*) Arg parsing should allow specific games in the database to be played
*) Unit tests would be nice
*) Game window should .... work
*) Game window should be tied into GM Window such that all values are reflected and 
    updated in real time
*) Should scrape more questions for the database
*) Remove g_obj from GameMasterWindow :D Since you can update the entire window by destroying it and then just repopulating it, "Next" can pass the object it was given to PopulateWindow,
    and just immediately start the whole process over again

# To test
*) new q/a from cli params
*) import db file from cli params
