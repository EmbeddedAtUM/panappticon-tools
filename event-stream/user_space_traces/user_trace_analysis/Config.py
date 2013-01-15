# Configurations

import os
import sys

result_path = './result'
user_id = 'faked_user' if len(sys.argv) == 1 else sys.argv[1]
thread_name_map_file_location = result_path + '/%s/thread_name_map' % user_id
webview_thread_map_file_location = result_path + '/%s/web_view_thread_map' % user_id
transaction_graphs_dir = result_path + '/%s/transactions/' % user_id
