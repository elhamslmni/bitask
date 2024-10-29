In this app, you can 
1- create new user
2- create new post
3- each user can rate each post
4- each user can see all posts with details

--------------------------------------------------------------------

* for substantial amount of requests we store average rate of each post
* in cache, the data will be available in cache about 1 hour,
* we don't care about changes in data until it is available in cache
* also we can use clickhouse to store rating data more efficiently

---------------------------------------------------------------------


* to avoid cheating, we first calculate average rating per day
* then we calculate average of averages
* in addition, we can give different weights to each day 
* regarded to its rate amount to make it more fair, 
* for instance if the average number of rates per day for a post is 20
* we can set weight 0.5 for days with less than 10 rates, 2 for more than
* 40 rates, 1 for others. in this approach while we don't ignore real biases,
* we prevent fake rating. there are several different approaches,
* it depends on the specific type of the app


----------------------------------------------------------------------

* we can also store all posts in cache to avoid numerous db requests

----------------------------------------------------------------------