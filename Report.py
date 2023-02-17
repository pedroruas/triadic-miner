# -*- coding: utf-8 -*-
"""
@author: pedroruas
"""

import os


class Report():

    def __init__(self, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name
        self.module_time = []
        self.sections = []

    def add_module_time(self, title, time):
        self.module_time.append({'module_name': title, 'time': time})

    def save_report(self):
        if not os.path.isdir("output/"):
            os.mkdir("output")
        file = open(self.file_path, 'w', encoding='utf-8')
        file.write(
            'EXECUTION REPORT FOR FILE: {0}\n\n\n'.format(self.file_name))

        total_time = 0
        for module in self.module_time:
            file.write('{0} took {1} seconds\n'.format(
                module['module_name'], '{:.4f}'.format(module['time'])))
            total_time += module['time']

        file.write('\nTotal time: {0} seconds (or {1} minutes, or {2} hours)\n'.format(
            '{:.4}'.format(total_time), '{:.4}'.format(total_time/60), '{:.4}'.format(total_time/3600)))
        file.close()
