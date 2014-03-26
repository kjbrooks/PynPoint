
# Copyright (C) 2014 ETH Zurich, Institute for Astronomy

"""
Tests for `PynPoint_v1_5` module basis.
"""
#from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
# import PynPoint_v1_5 as PynPoint
import PynPoint

import sys
import os
import numpy as np

limit0 = 1e-20
limit1 = 1e-10
limit2 = 2e-4

class TestPynpoint_v1_5(object):

    def setup(self):
        #prepare unit test. Load data etc
        print("setting up " + __name__)
        test_data = (os.path.dirname(__file__))+'/test_data/'
        print(test_data)
        self.test_data_dir = test_data
        self.files_fits = [test_data+'Cube_000_Frame_0002_zoom_2.0.fits_shift.fits_planet.fits',
        test_data+'Cube_001_Frame_0130_zoom_2.0.fits_shift.fits_planet.fits',
        test_data+'Cube_000_Frame_0166_zoom_2.0.fits_shift.fits_planet.fits',
        test_data+'Cube_003_Frame_0160_zoom_2.0.fits_shift.fits_planet.fits']
        self.file_hdf = test_data+'testfile_basis.hdf5'
        # self.file_hdf_restore = test_data+'testfile_basis.hdf5'
        self.files_fits_sorted = [self.files_fits[0],self.files_fits[2],self.files_fits[1],self.files_fits[3]]

        # self.basis1 = PynPoint.basis(self.test_data_dir,intype='dir',cent_remove=False,resize=False,ran_sub=False,recent=False)
        self.basis1 = PynPoint.basis.create_wdir(self.test_data_dir,
                                cent_remove=False,resize=False,ran_sub=False,recent=False)
        hdf5file = PynPoint.Util.filename4mdir(self.test_data_dir)
        self.basis5 = PynPoint.basis.create_whdf5input(hdf5file,
                                cent_remove=False,resize=False,ran_sub=False,recent=False)

        self.basis3 = PynPoint.basis.create_wdir(self.test_data_dir,
                                cent_remove=True,resize=False,ran_sub=False,recent=False)
        self.basis4 = PynPoint.basis.create_wdir(self.test_data_dir,
                                cent_remove=False,resize=True,F_int=4.0,F_final=2.0,ran_sub=False,recent=True)
        self.basisfits = PynPoint.basis.create_wfitsfiles(self.files_fits,
                                cent_remove=True,resize=False,ran_sub=False,recent=False)

        self.eg_array1 = np.arange(100.).reshape(4,5,5)
        self.ave_eg_array1 = np.array([[ 37.5,  38.5,  39.5,  40.5,  41.5],
                        [ 42.5,  43.5,  44.5,  45.5,  46.5],
                        [ 47.5,  48.5,  49.5,  50.5,  51.5],
                        [ 52.5,  53.5,  54.5,  55.5,  56.5],
                        [ 57.5,  58.5,  59.5,  60.5,  61.5]])
                        
        #second example array for testing the PCA parts
        self.eg_array2 = np.array([[ 0.75, -2.25, -0.25,  1.75],[ 0.5, -2.5, -0.5,  2.5],[-1.25,  3.75,  0.75, -3.25],[-2.25, -0.25,  0.75,  1.75]])
        self.eg_array2_pca = np.array([
                        [[-0.17410866485907938728 , 0.71893395614514299385],[ 0.11771735865682392275 ,-0.66254264994288725177]],
                        [[ 0.84800005432046565712 ,-0.13400452403625343067],[-0.29357897148679990007 ,-0.420416558797411688]],
                        [[-0.0241263485317723507 , 0.46387148461541644062],[-0.80619725314070234123 , 0.36645211705705693639]],
                        [[ 0.5        , 0.5       ],[ 0.5        , 0.5       ]]])
        self.eg_array2_coeff = np.array([
                        [ -2.937061877035140e+00 ,  2.751759847981489e-01 , -2.189650836484913e-01],
                        [ -3.599604526978027e+00 , -1.452405739992628e-01 ,  1.474870334085662e-01],
                        [  5.155189797925138e+00 , -4.163474455600442e-01 , -2.594131731843463e-02],
                        [ -8.591506115107919e-01 , -2.830412197722555e+00 , -2.504032196304351e-02],
                        [  1.00 ,  0.0  ,0.0],
                        [  0.0 ,  1.00  ,0.0],
                        [ 0.0 , 0.0  , 1.00000e+00],
                        [  0.0 , 0.0   , 0.0 ]])                 




        pass
        
    def test_save_restore(self,tmpdir):
        temp_file = str(tmpdir.join('tmp_hdf5.h5'))
        
        self.basis3.save(temp_file)
        temp_basis = PynPoint.basis.create_restore(temp_file)#('',intype='restore')
        # temp_basis.restore(temp_file)
        self.func4test_overall_same(self.basis3,temp_basis)
        
    def test_plt_orig(self):
        self.basis3.plt_orig(0)
        self.basis1.plt_orig(0)
            
    def test_plt_active(self):
        self.basis3.plt_active(0)
        
    def test_plt_pca(self):
        self.basis3.plt_pca(0)
    
    # def test_plt_pcarecon(self):
    #     x = 1
    #     assert x==1
        
    def test_anim_orig(self):
        self.basis3.anim_orig(num_frames = 3)
        self.basis3.anim_orig(num_frames = False)
        
    def test_anim_active(self):
        self.basis3.anim_active(num_frames = 3)
        self.basis3.anim_active(num_frames = False)
        
        
    def test_overall_basis3(self):
        assert np.array_equal(self.basis3.files , self.files_fits_sorted)
        assert self.basis3.num_files == len(self.basis3.files) 
        assert np.array_equal(self.basis3.im_size , (146,146))
        assert self.basis3.cent_remove is True
        assert self.basis3.im_arr.shape == (4,146,146) 
        assert np.allclose(self.basis3.im_arr.min() , -5.4805099807708757e-05,rtol=limit1)
        assert np.allclose(self.basis3.im_arr.max() , 6.2541826537199086e-05,rtol=limit1)
        assert np.allclose(self.basis3.im_arr.var() , 9.6723454568628155e-11 ,rtol=limit1)
        assert np.allclose(self.basis3.im_norm , np.array([ 2339855.10735457,  2484443.10731339 ,  2576155.10408142,  2167391.10663852]),rtol=limit1)
        assert np.array_equal(self.basis3.para , np.array([-17.3261, -17.172 , -17.0143, -16.6004]))
        assert self.basis3.cent_mask.shape == (146,146) 
        assert self.basis3.cent_mask.min() == 0.0 
        assert self.basis3.cent_mask.max() == 1.0
        assert self.basis3.cent_mask.var() == 0.22491619287271775 
        assert self.basis3.psf_basis.shape == (4,146,146) 
        #assert np.allclose(np.abs(self.basis3.psf_basis.min()), np.abs(-0.48548950237832555),rtol=limit2) 
        # assert self.basis3.psf_basis.max() == 0.81022092039077964
        assert np.allclose(self.basis3.psf_basis.var() , 4.6846490796021234e-05,rtol=limit1)
        assert self.basis3.im_ave.shape == (146,146)
        assert np.allclose(self.basis3.im_ave.min() , -2.4491993372066645e-05 ,rtol=limit1)
        assert np.allclose(self.basis3.im_ave.max() , 0.00013430662147584371,rtol=limit1)
        assert np.allclose(self.basis3.im_ave.var() , 2.1823141818009155e-10,rtol=limit1)
        
    def test_overall_basis1(self):
        basis = self.basis1
        basis_base = self.basis3
        #general comparisons with the baseline base instance
        assert np.array_equal(basis.files , basis_base.files) 
        assert basis.num_files == basis_base.num_files
        assert np.array_equal(basis.im_size , basis_base.im_size)
        assert np.array_equal(basis.im_arr.shape , basis_base.im_arr.shape)
        assert np.array_equal(basis.im_norm , basis_base.im_norm)

        assert np.array_equal(basis.im_arr.shape , (4,146,146) )
        assert np.allclose(basis.im_arr.min() , -0.00058314422494731843,rtol=limit1)
        assert np.allclose(basis.im_arr.max() , 0.00099531450541689992,rtol=limit1)
        assert np.allclose(basis.im_arr.var() , 9.0390377244261668e-10 ,rtol=limit1)
        assert basis.cent_remove is False
        assert np.array_equal(basis.cent_mask , np.ones(shape=(146,146)))  
        
        # assert np.array_equal(basis.basis_pca.shape , (4,146,146) )
        assert np.array_equal(basis.psf_basis.shape , (4,146,146) )
        # assert np.allclose(basis.psf_basis.min() , -0.87473462037563898 ,rtol=limit2)
        # assert np.allclose(basis.psf_basis.max() , 0.17821624402894418,rtol=limit2)
        assert np.allclose(basis.psf_basis.var() , 4.6912928533908474e-05,rtol=limit1)
        
    # def test_overall_basis2(self):
    #     basis = self.basis2
    #     basis_base = self.basis3
    #     #general comparisons with the baseline base instance
    #     assert len(basis.files) == 2 
    #     assert basis.num_files == len(basis.files)
    #     #could add extra tests
 
    def func4test_overall_same(self,basis,basis_base):
        assert np.array_equal(basis.files, basis_base.files) 
        assert np.array_equal(basis.num_files , basis_base.num_files)
        assert np.array_equal(basis.im_size,basis_base.im_size)
        assert basis.cent_remove  == basis_base.cent_remove 
        #assert basis.im_arr.shape[0] == basis_base.im_arr.shape[0]
        assert np.array_equal(basis.im_norm , basis_base.im_norm)
        #assert np.array_equal(basis.im_arr , basis_base.im_arr)#,atol=limit0)
        assert np.array_equal(basis.psf_basis , basis_base.psf_basis)#,atol=limit1)
        assert np.array_equal(basis.cent_mask,basis_base.cent_mask)
        assert np.array_equal(basis.im_ave,basis_base.im_ave)#,atol=limit1)
        
    def test_overall_basis5(self):
        self.func4test_overall_same(self.basis5,self.basis1)
    # 
    # def test_overall_basis_hdf(self):
    #     self.func4test_overall_same(self.basis_hdf,self.basis3)
    # 
       
    
    def teardown(self):
        #tidy up
        print("tearing down " + __name__)
        tempfilename = PynPoint.Util.filename4mdir(self.test_data_dir,filetype='convert')
        if os.path.isfile(tempfilename):
            os.remove(tempfilename)
        
        pass

# #if __name__ == "main":
# test = TestPynpoint_v1_5()
# test.setup()
# test.test_save_restore(None)


                   
    # def test_mk_pca(self):
    #     basis_test = PynPoint.basis('',intype='empty')
    #     a = self.eg_array2
    # 
    #     a_test = self.eg_array2_pca.reshape([4,2,2])
    # 
    #     basis_test.im_arr = a
    #     basis_test.im_size = [2,2]
    #     basis_test.num_files=4
    #     assert not hasattr(basis_test, 'basis_pca')
    #     basis_test.mk_pca()
    #     assert hasattr(basis_test, 'basis_pca')
    # 
    #     test_array = np.zeros([4,4])
    #     for i in range(0,4):
    #         for j in range(0,4):
    #             test_array[i,j] = (basis_test.basis_pca[i,].flatten()*basis_test.basis_pca[j,].flatten()).sum()                
    # 
    #     assert np.allclose(test_array,np.identity(4),rtol=limit1)
    #     assert np.allclose(basis_test.basis_pca,a_test,rtol=limit1)
        
          
    # def test_mk_pcafit_one(self):
    #     basis_test = PynPoint.basis('',intype='empty')
    #     a = self.eg_array2 
    #     basis_test.im_arr = a
    #     basis_test.im_size = [2,2]
    #     basis_test.num_files=4
    #     basis_test.cent_remove = False
    #     basis_test.basis_pca = self.eg_array2_pca #mk_pca()
    #     a_test = self.eg_array2_pca.reshape([4,4]) 
    #     im_test = np.vstack((a,a_test))                
    #     
    #     coeff = np.zeros(shape=(8,3))
    #     np.set_printoptions(precision=15)   
    #     test_coeff = self.eg_array2_coeff
    #     for i in range(0,8):
    #         coeff[i,] = basis_test.mk_pcafit_one(im_test[i].reshape((2,2)),num=3,meansub=False)
    #     assert np.allclose(coeff,test_coeff,rtol=limit1)
    #     
    # def test_mk_pcarecon(self):
    #     
    #     basis_test = PynPoint.basis('',intype='empty')
    #     basis_test.im_size = [2,2]
    #     basis_test.num_files=4
    #     basis_test.cent_remove = False
    #     basis_test.basis_pca = self.eg_array2_pca
    #     basis_test.im_ave = np.ones(shape = (2,2))*np.pi
    #     test_coeff = np.array([1.,2.,3.,4.])        
    #     temp = basis_test.mk_pcarecon(test_coeff,meanadd=False)
    #     print(test_coeff.shape)
    #     print(basis_test.basis_pca.reshape(4,4).shape)
    #     temp_test = np.dot(test_coeff,basis_test.basis_pca.reshape(4,4))
    #     print(temp.flatten())
    #     print(temp_test)
    #     assert np.allclose(temp.flatten(),temp_test,rtol=limit1)
    #     temp2 = basis_test.mk_pcarecon(test_coeff,meanadd=True)
    #     assert np.allclose(temp2.flatten(),temp_test+np.pi,rtol=limit1)
    #     
    # def test_mk_orig(self):
    #     x = 1
    #     assert x==1