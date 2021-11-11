# Tile Numbering
The main point here is to define the tile addressing. 
This addressing is used by the main loop regulation.


  ##FRONT VUE

| 15<br>(1111) | 14<br>(1110) | 13<br>(1101) | 12<br>(1100) |
|:------------:|:------------:|:------------:|:------------:|
| 11<br>(1011) | 10<br>(1010) |  9<br>(1001) |  8<br>(1000) |
|  7<br>(0111) |  6<br>(0110) |  5<br>(0101) |  4<br>(0100) |
|  3<br>(0011) |  2<br>(0010) |  1<br>(0001) |  0<br>(0000) |

The order is important here cause the LED Light strip is 
2.4 m long in one piece ! the addressing defines the order.

So it would be wiring in that order !

Also you can navigate in the order. 
If you want to go up or down just add/sub four.
if you want to go in line add/sub 1%4.

