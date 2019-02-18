# Reid_research
                                            Reid_Algorithm optimization
### Summary:
	Person re-identification has become a research hotspot in recent years, with 36 CVPR articles in 2018. My code is mainly for the construction of pedestrian recognition data set. Another project is the implementation of modified baseline and MGN in different frameworks. Because all the video sequences collected from the camera are video sequences, our idea is to parse the video data into pictures, seek similarity between pictures, and integrate the data into Makert1501 format.
### Use process:
	Reading the code of kgraph_main1.py carefully, this project introduces the concept of ANN, which transforms the problem of finding similarity N N of high-dimensional image vectors into ANN problem.（ANN：approximate nearest neighborhood），By modifying the path of cam1, CAM2 and candidate paths, as well as loading obj method and saving obj method, we can adapt to the format of our datasets.
### Detailed introduction:
	Because the project runs on the server, it requires high memory and graphics cards. The default configuration is that the memory requirement is greater than or equal to 32G, the computer is required to have eight cores, and the graphics cards are four, each of which is 11G.If your configuration is not so high, you need to see the kgraph_main1.py code, modify the places where there are multiple processes, and modify the code that runs on four graphics cards at the same time. My code can be applied to very large data sets. Gallery and query can contain hundreds of thousands of pictures, and each data vector can be 2048 dimensions.ps:After testing my data set, my code can greatly reduce the problem time of finding similarity from high-dimensional image data. NN searches in high-dimensional data for about 20 days, while my code only needs 12 hours.
	My code also provides an optimization idea for the algorithm. The NN problem of finding similarity from high-dimensional data has always been a difficult problem to solve. By borrowing the kgraph method of ANN, we can speed up the search speed and meet the requirements of the project online with slight loss of accuracy.
### ANN References:
ANN-benchmarks:https://github.com/erikbern/ann-benchmarks
Kgraph Library：https://github.com/aaalgo/kgraph
This code mainly focuses on data set cleaning and production, so several scripts have been written for use：
filter_image.py：Screening for non-conforming image size. For example, images with inconsistent width and height can be screened out.
filter_image.sh:Double-click the shell script that filters the data set directly.
transform_fileName.py：The data of the video sequence is sorted into the same day, but labeled differently.
To be continued......
		



    
