# Training the Mask Generator for Sclera 
## Code obtained from: https://github.com/milesial/Pytorch-UNet

1. Have same file names for images and masks. 
2. Store the images in imgs folder and masks in the masks folder, these are located in data folder. 
3. To train the model: 
```
python train.py 
```
4. To test the model:
```
python predict.py -i input_filename.png -o output_filename.png
```
5. Upon successfull training of the code, the models parameters will be saved in checkpoints/ directory. 