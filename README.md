# Algorithm to Recommend Scientific Papers

I wanted to built something that would make scientific papers accessible so I could keep up with new stuff happening in science. In the future, I want it to be something I could open instead of instagram almost like a cross between a tinder for scientific papers (the algorithm of which I tried to build in this project) and then an interface that makes reading papers accessible (ie like summaries or a built in definition tool).

This tool uses Crossref paper metadata and sorts it. It shows you one paper at a time then you can give feedback on the paper and from that it understands you better and can recommend you better things. 

You can run the project from a folder. Initially i didnt know how to ship this because i was running it in my ide. This version of the project can be tested by the github pages link which simulates a terminal. To make this I used references for how to do this but in general its a pretty short ui which runs in the browser so that you can see recs without installing anything. Eventually I think this could become an app by adding a cooler UI but istill need to figure out how to dob that.
ALl that said though, github pages running the python can be really really slow, so I recommend you run the file locally :) 

When youre running it, you can use a couple commands i.e. 
- `y` / `yes` which accept the paper
- `n` / `no` which  reject the paper
- `s` / `save` / `later` which save for later
- `l` / `list` which  show saved reading list
- `p` / `profile` which show feedback summary
- `q` / `quit` / `exit` which  quit the program


