### Instruction Set: Training with Yolov2

Here is the link to the [dataset](https://www.microsoft.com/en-us/research/project/msra-cfw-data-set-of-celebrity-faces-on-the-web/) of celebrity faces. The format of this dataset is a folder of for each celebrity, with one file in each folder that has the left/top/right/bottom of each image.

[Tutorial for training that we followed](https://timebutt.github.io/static/how-to-train-yolov2-to-detect-custom-objects/): this shows that yolo needs the data prepared in a different format and file structure. The first half of convert_bbox.py prepares this. It is specifically catered to the format of that dataset linked above. When future groups decide to continue training data sets, either they need to find a source with consistent labeling or modify the script every time for each new data set. Celebrities are the most relevant to the current state of the system so we chose to build around this set. The second half of the script prepares the test files and train file, as well as the configuration of the data.

The last part executes the training, which I believe goes for one thousand iterations. There is a way to add a backup so you can pause and continue retraining, but this isn't ideal for our pipeline. I'm guessing this may take a couple days (a lot of actors with a hundred images each) to process on a 1070. The weights get dropped into the directorym, but this is speculation since we've never seen the process complete fully.

So to pipeline the whole process:

1. Place the dataset into bboxIn (the script should populate bboxOut for yolo's use)
2. Count the number of classes you're adding and modify ../cfg/yolo-voc.cfg (on line 247)
3. Calculate the number of filters via the formula: FILTERS = (CLASSES + 5) * 5 on line 239 of ../cfg/yolo-voc.cfg
4. Run: python convert_bbox.py
5. Modify the populate database script to use these new weights and obj.data