import os 
import cv2 
import dlib
import tqdm
import torch 
import PIL.Image  
import numpy as np
from pathlib import Path
import torch.nn.functional as F
import matplotlib.pyplot as plt 

class Utils():
    def __init__(self) -> None:
        pass 
    
    @staticmethod
    def Load_image(image_path, CV2=True):
        """
        Parameters
        ----------
        image_path: str
            This string should contain a valid relative or absolute path
            to the image with filename. 
            i.e example/image.png 
        CV2 : boolean
            If CV2=True: Then OpenCV will be used to load the image 
            or else PIL.Image   
        Returns 
        -------   
        image : OpenCV or PIL.Image Object of your choice 

        Note
        ----
        OpenCV loads image in Blue Green Red (BGR) format 
        PIL loads image in Red Green Blue (RGB) format    
        """
        if CV2:
            img = cv2.imread(image_path)
        else:
            img = PIL.Image.open(image_path)
        return img

    @staticmethod
    def Save_image(img, image_path, CV2=True):
        """
        Parameters
        ----------
        img: OpenCV or PIL image
            Image object to be saved. 
            if the image is in PIL form please set CV2=False
        image_path: str
            This string should contain a valid relative or absolute path
            to the image with filename. Please note if a file exist with 
            that name it will be replaced 
            i.e example/image.png

        CV2: Boolean 
            If True, it will write an image using CV2,
            otherwise, PIL.Image 
        """
        if CV2:
            cv2.imwrite(image_path, img)
        else:
            img.save(image_path)

    @staticmethod
    def OpenCV_To_PIL(img):
        """
        Parameters
        ----------
        img: OpenCV Image - BGR format

        Return
        ---------
        img: PIL image - RGB format        
        """
        # Convert BGR to RGB 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convert it to PIL 
        img = PIL.Image.fromarray(img)
        
        return img 


    @staticmethod
    def PIL_To_OpenCV(img):
        """
        Parameters
        ----------
        img: PIL image - RGB format  
        
        Return
        ---------
        img: OpenCV Image - BGR format
        """
        # Convert PIL to Numpy 
        img = np.array(img)

        # Convert RGB to BGR 
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        return img

    @staticmethod 
    def Image_To_Histogram(image, bins=64, suppress_black=True, concat=False):
        """
        Parameters
        ----------
        image: OpenCV image 
            Image of anything 
        bins: int
            the number of subdivisions in each dim
        suppress_black : boolean 
            ignore black in histogram
        
        concat: if True:
            Returns a numpy array with size of bins * 3 

        Return
        ------
        hist: 3D Array 
            Contains the histogram calculated

        Notes 
        -----
        If the hist is being used for training, prefer 
        using hist.flatten() 
        """
        #cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

        # Compute the color histogram for the RGB image
        hist = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 255, 0, 255, 0, 255])
        

        if suppress_black:
            # Exclude the black color
            hist[0, 0, 0] = 0

        # Calculate the sum of all bins in the histogram
        total_sum = np.sum(hist)

        # Normalize the histogram by dividing each bin by the total sum
        hist /= total_sum

        # Reshape the histogram to a 3D array
        hist = hist.reshape(bins, bins, bins)

        if concat:
            red = np.sum(hist, axis=(0, 1))
            green = np.sum(hist, axis=(0, 2))
            blue = np.sum(hist, axis=(1, 2))
            c = np.concatenate([red, green, blue]) 
            return c

        return hist 

    @staticmethod
    def Display_Image_To_Histogram_Plot(image, save=False, path=''):
        """
        Parameters
        ----------
        image: OpenCV image 
            Image of anything 

        save : boolean 
            Saves the plot 
        
        path : str
            The path + filename + extension if save option is true.

        Returns
        -------
        hist : 3d array 
            The histogram 

        Note 
        ----
        Expect an error if save option is true and path is not valid 
        """
        hist = Utils.Image_To_Histogram(image)
        
        # Subplot for Red Channel 
        plt.subplot(311)
        plt.plot(np.sum(hist, axis=(0, 1)))
        plt.xlim([0, 64])
        plt.title("Red")
        
        # Subplot for Green Channel 
        plt.subplot(312)
        plt.plot(np.sum(hist, axis=(0, 2)))
        plt.xlim([0, 64])
        plt.title("Green")

        # Subplot for Blue Channel 
        plt.subplot(313)
        plt.plot(np.sum(hist, axis=(1, 2)))
        plt.xlim([0, 64])
        plt.title("Blue")

        if save: 
            if path == '':
                print("Specify Path!")
            else:              
                plt.savefig(path)
        
        # Show the plot 
        plt.show()

        return hist 




class Face():
    def __init__(self):
        pass

    @staticmethod
    def extract_eyes_landmark(img):
        """
        Parameters
        ----------
        img: OpenCV Image - BGR format
            The image should contain a face with two eyes. 

        Returns
        -------
        left: OpenCV Object - BGR format 
            Image of Left eye 
        right: OpenCV Object - BGR format 
            Image of Right eye 

        Notes
        --------
        The crop sizing should be adjusted with this method
        on non-standardised dataset. 

        Requires
        --------
        Dlib model  
            get_frontal_face_detector()
            shape predictor: can be obtained from here:
            https://www.kaggle.com/datasets/sergiovirahonda/shape-predictor-68-face-landmarksdat
        """
        # load model 
        detector = dlib.get_frontal_face_detector()
        path = os.path.join(
             Path(__file__).parent.absolute(),
             'classifiers', 
             'shape_predictor_68_face_landmarks.dat')
        predictor = dlib.shape_predictor(path)
        
        # Detect faces 
        faces = detector(img)
        for face in faces:
            # Facial Landmarks 
            landmarks = predictor(img, face)

            # Get the left and right eye coordinates
            left_eye_x = landmarks.part(36).x
            left_eye_y = landmarks.part(36).y
            right_eye_x = landmarks.part(45).x
            right_eye_y = landmarks.part(45).y

            # Crop the left eye
            left_eye_img = img[ left_eye_y-100:left_eye_y+100, 
                                left_eye_x-100:left_eye_x+400]

            # Crop the right eye
            right_eye_img = img[right_eye_y-100:right_eye_y+100, 
                                right_eye_x-400:right_eye_x+100]

        return left_eye_img, right_eye_img

    @staticmethod
    def extract_eyes_Bounded(img):
        """
        Parameters
        ----------
        img: OpenCV Image - BGR format
            The image should contain a face with two eyes. 

        Returns
        -------
        left: OpenCV Object - BGR format 
            Image of Left eye 
        right: OpenCV Object - BGR format 
            Image of Right eye 

        Notes
        --------
        It has the ability to produce inconsistent crop size. 
        Use case: For non-standardised images. 

        Requires
        --------
        OpenCV model: 
            haarcascade_eye.xml 
            can be obtained from: 
            https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
        """

        # Convert the image to gray scale 
        image_gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)

        path = os.path.join(
             Path(__file__).parent.absolute(),
             'classifiers', 
             'haarcascade_eye.xml')

        # Load the model 
        eye_bounded_detector = cv2.CascadeClassifier(path)
        eyes = eye_bounded_detector.detectMultiScale(image_gray)

        # Bound and extract left eye
        left = eyes[0]
        ex, ey, ew, eh = left 
        left_eye = img[ey:ey+eh, ex: ex+ew]

        # Bound and extract right eye 
        right = eyes[1]
        ex, ey, ew, eh = right 
        right_eye = img[ey:ey+eh, ex: ex+ew]
        
        return left_eye, right_eye


class Eye():
    def __init__(self) -> None:
        pass 

    @staticmethod
    def preprocess(mask_values, pil_img, scale, is_mask):
        """
        Parameters
        ----------
        mask_values : a list 
            consisting of different colour pixel range in the mask
            e.g [[0,0,0],[255,255,255]]
        
        pil_img : a PIL image 
            image of the eye (sclera)

        scale : float 
            upscale or downscale by factor of 'scale' 
        
        is_mask: Boolean 
            if the image is a mask or not
        

        Returns 
        -------
        img : PIL image 
            This is a preprocessed image. 

        Notes
        -----
        Function borrowed from:
        https://github.com/milesial/Pytorch-UNet       
        
        """
        w, h = pil_img.size
        newW, newH = int(scale * w), int(scale * h)
        assert newW > 0 and newH > 0, 'Scale is too small, resized images would have no pixel'
        pil_img = pil_img.resize((newW, newH), resample=PIL.Image.NEAREST if is_mask else PIL.Image.BICUBIC)
        img = np.asarray(pil_img)

        if is_mask:
            mask = np.zeros((newH, newW), dtype=np.int64)
            for i, v in enumerate(mask_values):
                if img.ndim == 2:
                    mask[img == v] = i
                else:
                    mask[(img == v).all(-1)] = i

            return mask

        else:
            if img.ndim == 2:
                img = img[np.newaxis, ...]
            else:
                img = img.transpose((2, 0, 1))

            if (img > 1).any():
                img = img / 255.0

            return img

    @staticmethod
    def predict_img(net,
            full_img,
            device,
            scale_factor=1,
            out_threshold=0.5):
        """
        Parameters
        ----------
        net: PyTorch model
            The model (UNet) required for segmentation 
        
        full_image: PIL image 
            Image of Eye which need to be converted to mask
        
        device: 'cpu' or 'cuda' 

        scale_factor: float 
            Scale factor of the image 

        Returns
        -------
        mask: Numpy object 

        Notes
        -----
        Function borrowed from:
        https://github.com/milesial/Pytorch-UNet       
        """
        
        net.eval()
        img = torch.from_numpy(Eye.preprocess(None, full_img, scale_factor, is_mask=False))
        img = img.unsqueeze(0)
        img = img.to(device=device, dtype=torch.float32)

        with torch.no_grad():
            output = net(img).cpu()
            output = F.interpolate(output, (full_img.size[1], full_img.size[0]), mode='bilinear')
            if net.n_classes > 1:
                mask = output.argmax(dim=1)
            else:
                mask = torch.sigmoid(output) > out_threshold

        return mask[0].long().squeeze().numpy()

    @staticmethod
    def mask_to_image(mask: np.ndarray, mask_values):
        """
        Parameters
        ----------
        mask: numpy array 
            Array connsisting of the values in the mask 
        mask_values : list 
            list containing list of colour channels present in the mask 
            i.e [[0,0,0], [255,255,255]]

        Returns 
        -------
        image : PIL image 
            mask image       

        Notes
        -----
        Function borrowed from:
        https://github.com/milesial/Pytorch-UNet         
        """
        if isinstance(mask_values[0], list):
            out = np.zeros((mask.shape[-2], mask.shape[-1], len(mask_values[0])), dtype=np.uint8)
        elif mask_values == [0, 1]:
            out = np.zeros((mask.shape[-2], mask.shape[-1]), dtype=bool)
        else:
            out = np.zeros((mask.shape[-2], mask.shape[-1]), dtype=np.uint8)

        if mask.ndim == 3:
            mask = np.argmax(mask, axis=0)

        for i, v in enumerate(mask_values):
            out[mask == i] = v

        return PIL.Image.fromarray(out)

    @staticmethod
    def Generate_EyeToMask(image, model, device):
        """
        Parameters
        ----------
        image: PIL Image 
            Image of the eye crop
        
        model: Pytorch model 
            PyTorch Model for Mask Generation 
        
        device: 'cpu' or 'cuda'
            Device for computation

        Return 
        ------
        image : PIL image 
            image of mask

        """
        # Predict the mask for the image 
        mask = Eye.predict_img(model, image, scale_factor=0.5, out_threshold=0.5, device=device)
        
        # Convert Mask to an Image 
        image = Eye.mask_to_image(mask, [[0,0,0],[255,255,255]])

        return image 
    
    @staticmethod
    def merge_image(background_image, foreground_image):
        """
        Parameters
        ----------
        background_iamge : OpenCV image 
            The eye crop 
        foreground_image : OpenCv Image 
            The mask image 
        
        Return 
        ------
        result_image : OpenCV image 
            Sclera Extracted Image 
        """
        result_image = background_image.copy() 
        foreground_mask = cv2.cvtColor(foreground_image, cv2.COLOR_BGR2GRAY)
        # Replace white colour 
        _, foreground_mask = cv2.threshold(foreground_mask, 255, 255, 255)
        result_image = cv2.bitwise_and(result_image, result_image, mask=foreground_mask)
        result_image = cv2.addWeighted(result_image, 0.5, foreground_image, 0, 0)
        
        return result_image

    @staticmethod
    def Face_To_LR_Sclera(image_path, 
        model_path= os.path.join(
             Path(__file__).parent.absolute(),
             'classifiers', 
             'ScleraMaskPredictor.pt'),
        device='cpu', retrieveCrops=False, preloaded=False):
        """
        Parameters
        ----------
        img_path : str 
            A valid absolute or relative path of the file, including filename 
            and its extension! 
        
        model_path: str
            A valid absolute or relative path of the file, including filename 
            and its extension! Pytorch file, pt
        
        device: 'cpu' or 'cuda' 
            For GUI choose CPU. 


        Returns 
        -------
        Left_Sclera : OpenCV obj 
            Contains the left sclera 
        Right_Sclera : OpenCV obj 
            Contains the right sclera 
        """
        
        # Load the images
        try:
            img = Utils.Load_image(image_path)
        except:
            raise Exception(f"Unable to load the image {image_path}")

        if preloaded == False:
            # Load Model 
            try: 
                model = torch.jit.load(model_path, map_location=torch.device(device))
            except:
                raise Exception(f"Unable to load the model at {model_path}")
        else:
            model = preloaded

        # Get the Eye Crops 
        try: 
            left, right = Face.extract_eyes_landmark(img)
        except:
            try:               
                left, right = Face.extract_eyes_Bounded(img)
            except:
                raise Exception(f"Unable to extract eyes from {image_path}")
        
        orignal_left, orignal_right = left.copy(), right.copy()

        # Generate Masks 
        try: 
            left_mask = Eye.Generate_EyeToMask(Utils.OpenCV_To_PIL(left),model, device)
            right_mask = Eye.Generate_EyeToMask(Utils.OpenCV_To_PIL(right), model,device)
        except: 
            raise Exception(f"Unable to generate masks from {image_path}")

        #Convert masks to OpenCV
        left_mask = Utils.PIL_To_OpenCV(left_mask)
        right_mask = Utils.PIL_To_OpenCV(right_mask)

        # Merge Mask with Eye Crops 
        try:
            left_sclera = Eye.merge_image(orignal_left, left_mask)
            right_sclera = Eye.merge_image(orignal_right, right_mask)
        except: 
            raise Exception(f"Unable to merge the sclera to mask {image_path}")
        
        if retrieveCrops: 
            return orignal_left, orignal_right, left_sclera, right_sclera
          
        return left_sclera, right_sclera


    @staticmethod
    def Save_Faces_To_Scleras(images, outputdir, model_path= os.path.join(
             Path(__file__).parent.absolute(),
             'classifiers', 
             'ScleraMaskPredictor.pt'), device=('cuda' if torch.cuda.is_available() else 'cpu')  ):
        """
        Parameters 
        ----------
        images : list 
            Contains all absolute path 
        output: str 
            Contains absolute path to dir of output. 
        Notes 
        -----
        If filenames have conflict in output directory they will be replaced 
        """
        print(f"Working on these images with help of {device}: ")
        
        # Load model: 
        try:           
            model = torch.jit.load(model_path, map_location=torch.device(device))
        except:
            print("Unable to load model!")
        for img in tqdm.tqdm( images): 
            failed =[]
            ff = 0 
            try: 
                l, r = Eye.Face_To_LR_Sclera(img, device=device, preloaded=model)
            except:
                ff += 1 
                failed.append(img)

            try: 
                filename = outputdir + os.path.basename(img).split('.')[0]
                Utils.Save_image(l, filename+"L.png")
                Utils.Save_image(r, filename+"R.png")
                #print(f"Filename processed and saved: {filename}")
            except:
                failed.append(f"Unable to save {img}!")
                
        print(f"{ff} failed:")
        for fail in failed: 
            print(f"\t {fail}")

    @staticmethod
    def _TO_Sclera(image_path, model_path=os.path.join(
             Path(__file__).parent.absolute(),
             'classifiers', 
             'ScleraMaskPredictor.pt'),
             device='cpu'):
        """
        """
        # Load the images
        try:
            img = Utils.Load_image(image_path)
        except:
            raise Exception(f"Unable to load the image {image_path}")


        original_img = img.copy()

        model = torch.jit.load(model_path, map_location=torch.device(device))

        # Generate Masks 
        try: 
            mask = Eye.Generate_EyeToMask( Utils.OpenCV_To_PIL(img), model, 'cpu')
        except: 
            raise Exception(f"Unable to generate masks from {image_path}")

        #Convert masks to OpenCV
        mask = Utils.PIL_To_OpenCV(mask)

        # Merge Mask with Eye Crops 
        try:
            sclera = Eye.merge_image(original_img, mask)
        except: 
            raise Exception(f"Unable to merge the sclera to mask {image_path}")
        
        return sclera 

    @staticmethod
    def Save_Eye_To_Sclera(images, output_dir):
        for img in images: 
            try: 
                sclera = Eye._TO_Sclera(img)
            except:
                raise Exception(f"Couldn't Process the {img}")

            try: 
                filename =  output_dir + os.path.basename(img).split('.')[0]
                Utils.Save_image(sclera, filename+".png")
                print(f"Filename processed and saved: {filename}")
            except:
                print(f"Unable to save {img}!")

