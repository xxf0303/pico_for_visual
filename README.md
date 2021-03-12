# quick start
  Here's a tutorial: How to get started with the project quickly on your PC! In this section, we'll show you how to install, run, and use our program to achieve the result shown in the following image:  
![1.png](https://i.loli.net/2021/03/12/FAxgiRrN3hlnLJO.png)
## Preparation     
Before you go through the steps below, your PC needs to be configured with Python 2.7 Plus.    
If your Pico version is listed in the figure below, you can take the next steps.
![2.png](https://i.loli.net/2021/03/12/G69JRKeQAqiDUfE.png)
## Configuration
### 1.Download pico-python
Enter this github website to download the codes you need.
<https://github.com/colinoflynn/pico-python>
### 2.Configuration of Pypi and Git
Execute the following statement:
```
pip install picoscope
git clone git@github.com:coliboflynn/pico-python.git
cd pico-python
```
### 3.Download PicoScope software or SDK
Enter this website and download the latest version of PicoScope software or SDK according to your Pico version.
<https://www.picotech.com/downloads>
## Run the program
### 1.Open "pico_Win.py"or"readingMode.py",
If you have to require the new data through Pico,connect Pico to you PC and open"pico_Win.py"  
Or if you already have the data you need to monitor,open "readingMode.py"and change the path to yours.In this way,the time consumption of the process will be greatly decreased.  
install the libraries needed to run this program in setting.
### 2.Run the program
And you will see this interface:
![3.png](https://i.loli.net/2021/03/12/Sp1JbUPDrgHsCxT.png)
### 3.Set the parameters
Follow the prompt bar on the left, enter the parameter value you want in the "INPUT" window, click "Settings" on the right, and get the following interface:
![4.png](https://i.loli.net/2021/03/12/TRStFhbP9CEzOpd.png)

In this interface, you can manipulate the size and extent of the image through the Keyboard in the lower left corner.
### 3.Grab partial curve
In order to grab an image of a specific phase, enter the phase range you want to observe in the lower left position phase window, click Settings, will jump out of the new window 2, with phase angle input 30-60 as an example:
![5.png](https://i.loli.net/2021/03/12/AEwsz6ChS9gMcLa.png)
#Authors,Reference and Thanks
Authors:     
Xiaofan Xia <xxf0303@sjtu.edu.cn>    
Yichen Sha <syc_chen@sjtu.edu.cn>    

Reference:  
Colin O'Flynn  
<https://github.com/colinoflynn/pico-python>

Thanks to our mentor Gang Zhao <nmzhaogang@sjtu.edu.cn>
