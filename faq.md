# FAQ

### How does the Auto Position Change work?
Once started, the Auto Position Change goes to sleep for the defined time and upon wakeup, it moves the table to the first position. After this, it goes to sleep again for the given interval. Upon the next wakeup, it moves the table to the next defined position (height). And so on, until the last position is reached. After the last position it starts from the first position again. 

### Does the Auto Position Change automatically stop if i move the table manually?
No, once activated, the Auto Position Change runs as long as you do not terminate it manually. So even if you move the table manually or using the ESPHome Web Interface, the Auto Position Change goes on. 

