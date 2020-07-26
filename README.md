# Switcheroo

Monitor unauthorized SSH login attempts... with a twist.


Log output:

```
2020-07-26T08:55:13.420897+00:00 auth='password' host='222.186.31.83' username='root' password='cacat123' valid='false'
2020-07-26T08:55:42.839670+00:00 auth='password' host='186.225.80.194' username='m1' password='123456' valid='false'
2020-07-26T08:57:20.689612+00:00 auth='password' host='222.186.31.83' username='root' password='123456' valid='false'
2020-07-26T08:57:34.839120+00:00 auth='password' host='218.92.0.204' username='root' password='aptx4869' valid='false'
2020-07-26T08:58:11.592082+00:00 auth='password' host='186.225.80.194' username='shadow' password='shadow' valid='false'
2020-07-26T08:58:38.680120+00:00 auth='password' host='112.85.42.104' username='root' password='dolphin1' valid='false'
2020-07-26T09:01:55.930339+00:00 auth='password' host='87.251.74.30' username='root' password='root' valid='false'
```


## The twist

Use the source luke.



## Docker

```
docker build --network=host -t switcheroo .
docker run --rm --network=host switcheroo
ssh root@127.0.0.1 -p10022
```
