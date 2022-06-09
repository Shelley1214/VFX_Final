#include <iostream>
#include <omp.h>
#include <math.h> 


double* Function(int *boundary, int *inner_pixel, double*diff, int X, int Y, int C)
{

    double* R = new double[X*C]();

    #pragma omp parallel for
    for (int i=0; i<X; i++){
        int * prev_vec = new int[2];
        prev_vec[0] = boundary[0] - inner_pixel[i*2+1];
        prev_vec[1] = boundary[1] - inner_pixel[i*2];
        double tan_val[Y][2];
        double Lambda[Y];
        double sum = 0;

        for (int j=1; j<Y+1; j++){
            int * vec = new int[2];
            vec[0] = boundary[j*2] - inner_pixel[i*2+1];
            vec[1] = boundary[j*2+1] - inner_pixel[i*2];
            double cosine_angle = (prev_vec[0]* vec[0] + prev_vec[1]* vec[1]) / ( sqrt(vec[0]*vec[0] + vec[1]*vec[1]) * sqrt(prev_vec[0]*prev_vec[0] + prev_vec[1]*prev_vec[1]) );
            cosine_angle = std::max(double(-1), std::min(cosine_angle, double(1)));
            tan_val[j-1][0] = tan(acos(cosine_angle)/2);
            tan_val[j-1][1] = sqrt(prev_vec[0]*prev_vec[0] + prev_vec[1]*prev_vec[1]);
            prev_vec = vec;
        }

        #pragma omp parallel for
        for(int j=0; j<Y; j++){
            double tan[2] = {tan_val[j][0], tan_val[ (j+Y-1)%Y][0]};
            double w = (tan[0]+tan[1]) / tan_val[j][1];
            sum += w;
            Lambda[j] = w;
        }

        for(int j=0; j<Y; j++){
            for (int c=0; c<C; c++){
                R[ i*C + c] += Lambda[j]/sum * diff[  j*C + c ];
            }
        }
    }

    return R;
}

extern "C" {
    double* MVC_Function(int *boundary, int *inner_pixel, double*diff, int X, int Y, int C)
    {
        return Function(boundary, inner_pixel, diff, X, Y, C);
    }

    void dealloc(double *ptr )
    {
        delete[] ptr;
    }
}