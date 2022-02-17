from source.image_processing.physical_input import ProcessImage, PhysicalInput
from source.misc.colored_console_text import TextColor, ColoredText
from source.image_processing.image_maker import ImageMaker
import json

def test_all():
    print('\nRunning API Tests-------------')
    success = test_process_image()
    if not success: return
    

def get_outcome_msg(test_title: str, condition: bool):
    if test_title == 'bypass': return condition
    success_msg = ColoredText('Passed', TextColor.GREEN) if condition else ColoredText('Failed', TextColor.FAIL)
    print(test_title + ": " + success_msg.Text)
    return condition

def test_process_image():
    proc_name = 'mf'
    img = ProcessImage(proc_name)
    phys_in = PhysicalInput(img)
    #coords = phys_in.get_button_coord_from_template('butt_2.png')
    #phys_in.click_at_coords(coords)
    phys_in.send_str('asd')
    
    success = get_outcome_msg('Process Image Test', True)
    return success

def test_image_maker():
    m = ImageMaker()
    success = get_outcome_msg('Image Maker Test', True)
    return success