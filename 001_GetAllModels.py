import easyocr
lan_lst = ['abq','ady','af','ang','ar','as','ava','az','be','bg','bh','bho','bn','bs','ch_sim','ch_tra','che','cs','cy','da','dar','de','en','es','et','fa','fr','ga','gom','hi','hr','hu','id','inh','is','it','ja','kbd','kn','ko','ku','la','lbe','lez','lt','lv','mah','mai','mi','mn','mr','ms','mt','ne','new','nl','no','oc','pi','pl','pt','ro','ru','rs_cyrillic','rs_latin','sck','sk','sl','sq','sv','sw','ta','tab','te','th','tjk','tl','tr','ug','uk','ur','uz','vi']
for i in range(len(lan_lst)):
    reader = easyocr.Reader([lan_lst[i]],gpu=False,model_storage_directory="SailModels") # need to run only once to load model into memory
#result = reader.readtext('chinese.jpg')

print("download Done")

