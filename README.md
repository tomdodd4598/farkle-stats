Farkle Calculator
=================


Summary
-------

A Python script which calculates the optimal decisions for a single turn in the dice game Farkle. Note that this program is only concerned with optimising the score obtained in a single, isolated turn; it does not necessarily produce the optimal decisions for particular scenarios against other players.

The algorithm used is based on [Matt Busche's blog post](http://www.mattbusche.org/blog/article/zilch/) about the very similar game of Zilch, and produces expected values of rolls in agreement with [possiblywrong's blog post](https://possiblywrong.wordpress.com/2013/04/07/analysis-of-farkle/).

A few settings exist which can be easily modified, and data from the most recent run will be cached so that it can be loaded if the properties of the game haven't been changed (there is a `no_cache` version of the script for running in places such as online interpreters).


Permissions
-----------

In practice, the license on any code I write means very little, but for those who want a some semblance of formality, let it be stated that all code is available under the [MIT License](https://github.com/tomdodd4598/farkle-stats/blob/main/LICENSE.md).