## Folder Structure
```
[code]/
  ├──[image]
  ├── main.py
  ├── ...
  └── README
```
  
## Environment

* Install the python dependencies on the virtual environment:

  ``` 
  pip install -r requirements.txt
  ```

## How to run

* We use OpenMP to speed up the program. To compile the cpp file, navigate to ```code``` directory and run ```make``` 
  or 
  ```
  g++ mvc.cpp -fopenmp -fPIC -shared -o mvc.so
  ```
    
  Python file can then call C++ code with ctypes module:
   
    ```
    python main.py
    ```

    
## Reference 
* Code
    * https://github.com/Tony-Tseng/vfx_final_project
    * https://github.com/MarcoForte/poisson-matting
    * https://github.com/ZheyuanXie/KLT-Feature-Tracking
* Paper
    * https://www.cs.huji.ac.il/~danix/mvclone/
