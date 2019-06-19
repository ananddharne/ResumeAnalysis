#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 13:27:57 2018

@author: himanshu
"""

import os 
import sys
from tkinter import *
import tkinter.font as tkFont
import pandas as pd
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from read_input import read_docx_and_pdf 

line_labels = {0: 'experience', 1: 'knowledge', 2: 'education', 3: 'project', 4: 'others'}
line_labels_reverse = {v:k for k,v in line_labels.items()}
line_types = {0: 'header', 1: 'meta', 2: 'content'}
line_types_reverse = {v:k for k,v in line_types.items()}

class AnnotatorGui(Frame):
    def __init__(self, master , lines_with_dummy_labels):
        Frame.__init__(self, master = master)
        self.CustomFont = tkFont.Font(family = 'Helvetica', size = 5)
        # self.master.title('Label Resume Lines')
        self.master.rowconfigure(0,weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.grid(sticky = W + E + N + S)
        self.lineIndex_list = []
        self.lineContent_list = []
        self.type_button_list = []
        self.label_button_list = []
        
        for line_number, line in enumerate(lines_with_dummy_labels):
            self.build_line(lines_with_dummy_labels, line_number, line)
        
        self.rowconfigure(1, weight = 1)
        self.columnconfigure(1, weight = 1)
        
    def build_line(self, table_content, line_index, line):
        line_content = line[0]

        line_index_label = Label(self.master, width=10, height=1, text=str(line_index))
        self.master.create_window(50, line_index*35, height=40, width=80, window=line_index_label)

        line_content_text = Text(self.master, width=100, height=1)
        line_content_text.insert(INSERT, line_content)
        self.master.create_window(1100, line_index*35, height=40, width=2000, window=line_content_text)

        def line_type_button_click(_line_index):
            line_type = table_content[_line_index][1]
            line_type = (line_type + 1) % len(line_types)
            table_content[_line_index][1] = line_type
            line_type_button["text"] = "Type: " + line_types[line_type]

        def line_label_button_click(_line_index):
            line_label = table_content[_line_index][2]
            line_label = (line_label + 1) % len(line_labels)
            table_content[_line_index][2] = line_label
            line_label_button["text"] = "Type: " + line_labels[line_label]

        line_type_button = Button(self.master, text="Type: Unknown", width=20,
                                  command=lambda: line_type_button_click(line_index))
        self.master.create_window(1500, line_index*35, height=40, width=300, window=line_type_button)
        line_label_button = Button(self.master, text='Label: Unknown', width=20,
                                   command=lambda: line_label_button_click(line_index))
        self.master.create_window(1800, line_index*35, height=40, width=300, window=line_label_button)


        if line[1] != -1:
            line_type_button["text"] = "Type: " + line_types[line[1]]
        if line[2] != -1:
            line_label_button["text"] = "Type: " + line_labels[line[2]]


def guess_line_type(line):
    return -1


def guess_line_label(line):
    return -1

def gui_annotate(training_data_dir_path, index, file_path, file_content):

    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    canvas = Canvas(root, width=170, height=300)
    vsb = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.grid(row=0, column=0, sticky=W+E+N+S)
    vsb.grid(row=0, column=1, sticky=N+S)

    table_content = [[line, guess_line_type(line), guess_line_label(line)] for line in file_content]
    gui = AnnotatorGui(canvas, table_content)

    def callback():
        root.destroy()
        output_file_path = os.path.join(training_data_dir_path, str(index)+'.csv')
        if os.path.exists(output_file_path):
            return
        data = pd.DataFrame.from_records(table_content,columns = ['text','type','label'])
        rows_to_drop = data.loc[((data['type']== -1) | (data['label'] == -1))].index
        data.drop(data.index[rows_to_drop],inplace = True,axis = 0)
        data.to_csv(output_file_path,index = False)

    # Define scrollregion AFTER widgets are placed on canvas
    canvas.config(yscrollcommand= vsb.set, scrollregion=canvas.bbox("all"))

    root.protocol("WM_DELETE_WINDOW", callback)
    root.mainloop()

def main():
    data_dir_path = os.path.abspath(__file__ + '/../../' + '/data')  # directory to scan for any pdf and docx files
    training_data_dir_path = data_dir_path + '/training_data'
    
    collected = read_docx_and_pdf(training_data_dir_path, verbose =True, callback=lambda index, file_path, file_content: {
        gui_annotate(training_data_dir_path, index, file_path, file_content)
    })
    
    print('count: ', len(collected))


if __name__ == '__main__':
    main()
       