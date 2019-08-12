import feather
import argparse
import pandas as pd

def feather_convert_args():
    parser = argparse.ArgumentParser(description='Useful functions for converting between feather and csv')
    parser.add_argument('-i','--input',type=str,required=True,help="filepath to input feather or csv file. (If .feather, will convert to csv and visa versa)")
    parser.add_argument('-o','--output',type=str,required=True, help="filepath to output feather or csv file. (If .feather, will convert to csv and visa versa)")
    args = vars(parser.parse_args())
    return(args)

def main():
    args=feather_convert_args()
    input_filepath = args["input"]
    output_filepath = args["output"]
    if ((".feather" in input_filepath) and (".csv" in output_filepath)):
        feather_to_csv(input_filepath,output_filepath)
    elif ((".csv" in input_filepath) and (".feather" in output_filepath)):
        feather_data = csv_to_feather(input_filepath,output_filepath)
        save_feather(feather_data,output_filepath)
    else:
        raise Exception("Invalid input or output filepath")

def feather_to_csv(feather_filepath,csv_filepath):
    feather_data = feather.read_dataframe(feather_filepath)
    feather_data.to_csv(csv_filepath)

def csv_to_feather(csv_filepath,feather_filepath):
    feather_data = pd.read_csv(csv_filepath)
    return feather_data

def save_feather(feather_data,feather_filepath):
    feather.write_dataframe(feather_data, feather_filepath)
    