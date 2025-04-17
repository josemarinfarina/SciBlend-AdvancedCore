from paraview.simple import GetActiveSource, GetActiveViewOrCreate, Show
from paraview.simple import GetAnimationScene, GetTimeKeeper, SaveData
import os
import sys

if len(sys.argv) > 3:
    folder_selected = sys.argv[1]
    start_frame = int(sys.argv[2])
    end_frame = int(sys.argv[3])
else:
    folder_selected = input("Save folder path: ")
    start_frame = int(input("Start frame (inclusive): "))
    end_frame = int(input("End frame (inclusive): "))

if os.path.isdir(folder_selected):
    selected_object = GetActiveSource()
    
    if selected_object:
        renderView = GetActiveViewOrCreate('RenderView')
        display = Show(selected_object, renderView)
        animationScene = GetAnimationScene()
        timeKeeper = GetTimeKeeper()
        animationScene.UpdateAnimationUsingDataTimeSteps()
        
        renderView.UseLight = 0
        renderView.CameraParallelProjection = 1
        
        time_values = timeKeeper.TimestepValues
        total_frames = len(time_values)
        
        if start_frame < 1 or end_frame > total_frames or start_frame > end_frame:
            print(f"Invalid range. Available frames: 1-{total_frames}")
            sys.exit()
            
        for frame_num in range(start_frame, end_frame + 1):
            idx = frame_num - 1
            current_time = time_values[idx]
            animationScene.TimeKeeper.Time = current_time
            renderView.Update()
            
            file_path = os.path.join(folder_selected, f"tempfile{frame_num}.vtk")
            SaveData(file_path, proxy=selected_object)
            
            print(f"Exported frame {frame_num} â {file_path}")
    else:
        print("No active object found")
else:
    print("Invalid directory")
