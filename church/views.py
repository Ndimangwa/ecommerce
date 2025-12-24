from django.shortcuts import render, redirect
from django.conf import settings
import os
import pandas as pd

church_name="Gorfan SDA Church"
# Create your views here.
def load_by_name(request):
    file_path = os.path.join(settings.BASE_DIR, '__my_church_data__', 'viongozi_2026.csv')
    context = {"church_name" : church_name}
    try:
        data = pd.read_csv(file_path, sep='|')
        if "Jina" not in data.columns:
            raise Exception("Jina not found in a column")
        list_of_names = data['Jina'].unique().tolist()
        list_of_names.sort(key=str)
        context['list_of_names'] = list_of_names
        #Now if this is POST we need to append , list of position
        if request.method == "POST":
            selected_name = request.POST['selected_name']
            if "Nafasi" not in data.columns:
                raise Exception("Nafasi not found in a column")
            selected_records = data[data['Jina']==selected_name]
            list_of_positions = selected_records['Nafasi'].tolist();
            list_of_positions.sort(key=str)
            context['list_of_positions'] = list_of_positions
    except FileNotFoundError:
        context['data'] = "File Not Found"
    except Exception as e:
        context['data'] = "General Error"
    return render(request, "church/load_by_name.html", context)

def load_by_position(request):
    return render(request, "church/load_by_position.html", {})