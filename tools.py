# -*- coding: utf-8 -*-

import pyogrio
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import rasterio




# vector import
def vec_import(engine, src):

  if engine == 'pyogrio':
    gdf_temp = pyogrio.read_dataframe(src)

  elif engine == 'gpd':
    gdf_temp = gpd.read_file(src)

  print('Vector import complete.')
  print('GDF size:{}'.format(len(gdf_temp)))
  print(gdf_temp.crs)
  
  return(gdf_temp)






# vector export
def vec_export(engine, tar_gdf, path):

  if engine == 'pyogrio':
    pyogrio.write_dataframe(
        tar_gdf,
        path,
        driver = "ESRI Shapefile",
        spatial_index =  False
    )

  elif engine == 'gpd':
    tar_gdf.to_file(path,
                  driver = 'ESRI Shapefile'
    )

  return (print('Vector export complete.'))






def addVecGeoCentroid(tar_gdf, crs_UTM):

  # Convert the spatial referenct to UTM if it is not
  if tar_gdf.crs != crs_UTM:
    tar_gdf = tar_gdf.to_crs(crs_UTM)


  # Create a deep copy of 'original'
  gdf_withCentroid = tar_gdf.copy()

  # Adding attributes to the shapefile: geomerty
  gdf_withCentroid['centroid'] = gdf_withCentroid['geometry'].centroid


  print('Output GDF size = {}'.format(len(gdf_withCentroid.index)))

  return(gdf_withCentroid)






# Raster Data Prep for Multi-Processing
def multiProcessDictPrep(num_process, input_df, tar_list, out_path, crs_UTM):

  print('No, of available CPU(s) = {}'.format(num_process))

  #Input dictionary prep for multiprocessing
  dict_input = []

  for i in range(1, (num_process + 1)):

      len_total_df = len(input_df)
      chunk = int(np.ceil(len_total_df / num_process))
      d_f = input_df[(chunk*(i-1)):(chunk*i)]

      dict_temp = {
          'df':d_f,
          'process_no':i,
      }

      dict_input.append(dict_temp)


  #Divide the dict_input into the input_items by the number of available CPU(s).
  input_items = []

  for i in range(num_process):
    print('Process No. = {}'.format(i))

    input_items.append((dict_input[i], tar_list, out_path, crs_UTM))


  return(input_items)







# Organizing the Raster Multi-Process results to a GDF
def multiProcessOrganizer_Raster(num_process, MP_results, gdf_original, tar_ras, on, how):

  df_out = pd.DataFrame()

  for i in range(num_process):

      df_temp = pd.DataFrame(MP_results[i])
      df_out = pd.concat([df_out, df_temp])


  gdf_preProcess = gdf_original.copy()

  for src in tar_ras:

      tar_col = src + '_val'
      df_out_temp = df_out.loc[df_out.CATE == src, ['PID', tar_col]]

      gdf_preProcess = pd.merge(gdf_preProcess, df_out_temp, on=on, how=how)

  return(gdf_preProcess)








# Organizing the vec2grid Multi-Process results to a GDF

def multiProcessOrganizer_vec2grid(num_process, MP_results, gdf_original, tar_vec, on, how):

  df_out = pd.DataFrame()

  for i in range(num_process):
      
      df_temp = pd.DataFrame(MP_results[i])
      df_out = pd.concat([df_out, df_temp])


  tar_col_list = ['PID'] + tar_vec

  df_out_merge = df_out.loc[:, tar_col_list].copy()

  df_out_merge.fillna(0, inplace = True)  


  grid_temp = gdf_original.copy()
  grid_temp = pd.merge(grid_temp, df_out_merge, on=on, how=how)

  return(grid_temp)








def urbanEvolution(tar_gdf):
  ## Classifying the building time estimation

  gdf_out = pd.DataFrame()

  tar_gdf['estimated_time'] = ""
  tar_gdf['wsfEvo_val'] = tar_gdf['wsfEvo_val'].astype('int')

  #Step-1 (2020-2023)
  gdf_temp = tar_gdf.query("wsfEvo_val == 0 & wsf2019_val == 0").copy()
  gdf_temp['estimated_time'] = '2020-2023'

  len20_23 = len(gdf_temp)
  print("Size (2020-2023) = {}".format(len20_23))

  gdf_out = pd.concat([gdf_out, gdf_temp])


  #Step-2 (2016-2019)
  gdf_temp = tar_gdf.query("wsfEvo_val == 0 & wsf2019_val == 255").copy()
  gdf_temp['estimated_time'] = '2016-2019'

  len16_19 = len(gdf_temp)
  print("Size (2016-2019) = {}".format(len16_19))

  gdf_out = pd.concat([gdf_out, gdf_temp])


  #Step-3 (1985-2015)
  gdf_temp = tar_gdf.query("wsfEvo_val > 0").copy()
  gdf_temp['estimated_time'] = gdf_temp['wsfEvo_val']

  len85_15 = len(gdf_temp)
  print("Size (1985-2015) = {}".format(len85_15))

  gdf_out = pd.concat([gdf_out, gdf_temp])


  #Sort values
  gdf_out.sort_values('PID', inplace = True)

  print("SUM = {}".format(len20_23 + len16_19 + len85_15))

  return(gdf_out)








def areaDensity(tar_vec, gdf):

  for tarVec in tar_vec:
    print('Area density calculation for {}'.format(tarVec))
    
    newCol = tarVec + '_dens'
    gdf[newCol] = gdf[tarVec] / gdf['area']
    

  # Converting the grid-temp layer to the complete_grid layer by omitting interim cols.
  tar_col_list_complete = ['geometry']

  for tarVec in tar_vec:
      newCol = tarVec + '_dens'
      tar_col_list_complete.append(newCol)

  areaDensGrid = gdf.loc[:, tar_col_list_complete].copy()

  return(areaDensGrid)








def vec2vec_distance(gdf_points, gdf_lines, tar_line_name):

  gdf_lines_temp = gdf_lines.copy()
  gdf_lines_temp['line_PID'] = gdf_lines_temp.index + 1
  gdf_lines_temp = gdf_lines_temp[['line_PID', 'geometry']]

  point_CRS = gdf_points.crs
  line_CRS = gdf_lines_temp.crs

  if not point_CRS == line_CRS:
    print('Unmatched CRS!: Process terminated')

  else:
    print('CRS check - OK --- POINTS = {} & LINES = {}: Proceed --> {}'.format(point_CRS, line_CRS, tar_line_name))

    gdf_ans = gpd.sjoin_nearest(gdf_points, gdf_lines_temp).merge(gdf_lines_temp, left_on="index_right", right_index=True)
    gdf_ans["distance"] = gdf_ans.apply(lambda r: r["geometry_x"].distance(r["geometry_y"]), axis=1)

    gdf_ans = gdf_ans[['PID', 'distance']]

    col_name = 'dist2' + tar_line_name
    gdf_ans = gdf_ans.rename(columns={'distance': col_name})

    gdf_ans = gdf_ans.drop_duplicates()

    return gdf_ans







def sentinelClip(s, bands, band_labels, out_path):

  ras_template = s
  band_label_num = 0

  for band in bands:

    print('Sentinel clipping: Band {} / {}'.format(band, band_labels[band_label_num]))
    
    ras_temp = s.read(band)

    outPath_ras = os.path.join(out_path, 'clip_' + band_labels[band_label_num] + '.tif')
    band_label_num += 1

    of=rasterio.open(outPath_ras,
                    'w',
                    driver='GTiff',
                    height=ras_temp.shape[0],
                    width=ras_temp.shape[1],
                    count=1,
                    dtype=ras_temp.dtype,
                    crs=ras_template.crs,
                    transform=ras_template.transform)

    of.write(ras_temp, 1)
    of.close()
