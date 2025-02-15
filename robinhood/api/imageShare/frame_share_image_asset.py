from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from urllib.request import urlopen
import io
import frappe

@frappe.whitelist()
def frameShareImageAsset (img_id, drive_count, full_name):
    # Set global variables values
    # Define the colors for the gradient
    color1 = (0, 100, 40)
    color2 = (0, 71, 77)
    font_family_url = 'https://checkin.robinhoodarmy.com/assets/robinhood/fonts/Inter-ExtraBold.ttf'
    padding = 160
    margin = 60
    border_radius = 30
    container_size = (800, 1450)
    container_width, container_height = container_size
    used_height = 0
    
    # ~~~~~~~~ Drive details ~~~~~~~~~~~~~~~~~~~~~
    # get the drive image
    image_response = requests.get('https://checkin.robinhoodarmy.com' + img_id )
    user_image = Image.open(io.BytesIO(image_response.content))
    image = user_image
    # get badge_text and badge image path based on drive count
    drive_count = int(drive_count)
    badge_text, badge_img_path = get_badge_details(drive_count)
    # ~~~~~~~~ End: Drive details ~~~~~~~~~~~~~~~~~~~~~

    # ################## Start: Decorate the image ##################
    # create gradient container image ~~~~~~~~~~~~~~~~~~~~~
    container = create_gradient_image(container_size, color1, color2)

    # ~~~~~~~~~~ logo image ~~~~~~~~~~~~
    # Put the logo image
    rha_logo_response = requests.get('https://checkin.robinhoodarmy.com/assets/robinhood/images/rha-logo.png' )
    rha_logo_img = Image.open(io.BytesIO(rha_logo_response.content))
    # resize the logo image
    new_size = tuple(dim - padding*2.2 for dim in container_size)
    # new_size = tuple(dim // 1.6 for dim in container_size)
    rha_logo_img.thumbnail(new_size)

    # paste the logo image in the center of the container
    logo_width, logo_height = rha_logo_img.size
    x = (container_width - logo_width) // 2
    y = int(used_height + margin)
    container.paste(rha_logo_img, (x, y))
    used_height = y + logo_height
    # ~~~~~~~~~~ end: logo image ~~~~~~~~~~~~

    # ~~~~~~~~~~ image ~~~~~~~~~~~~
    # Crop the image
    # Define crop dimensions
    crop_width, crop_height = 620, 650
    image = ImageOps.fit(image, (crop_width, crop_height), Image.ANTIALIAS)
    border_radius = 80
    image = put_border_radius(image, border_radius)

    # paste image in container at the center
    image_width, image_height = image.size
    x = (container_width - image_width) // 2
    y = int(used_height + margin*0.75)
    container.paste(image, (x, y), image)
    used_height = y + image_height
    # ~~~~~~~~~~ end: image ~~~~~~~~~~~~


    # ~~~~~~~~~~ Badge image ~~~~~~~~~~~~
    badge_image_response = requests.get('https://checkin.robinhoodarmy.com/assets/robinhood/badges/'+badge_img_path+'.png' )
    badge_image = Image.open(io.BytesIO(badge_image_response.content))
    # resize the badge_image
    new_size = tuple(dim // 4 for dim in image.size)
    badge_image.thumbnail(new_size)
    # paste image in container at the center
    image_width, image_height = badge_image.size
    x = (container_width - image_width) // 2
    y = int(used_height - margin*1.4)
    container.paste(badge_image, (x, y), badge_image)
    used_height = y + image_height
    # ~~~~~~~~~~ end: Badge image ~~~~~~~~~~~~

    # ~~~~~~~~~~ Text: name text ~~~~~~~~~~~~
    # Add text to the container using the ImageDraw module
    draw = ImageDraw.Draw(container)
    text = f"{full_name.upper()}"
    font = ImageFont.truetype(urlopen(font_family_url), 40)
    # get text box size
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = (
        text_box[2] - text_box[0]), (text_box[3] - text_box[1])
    x = (container.width - text_width) / 2
    y = int(used_height + margin*0.5)
    draw.text((x, y), text, font=font, fill=(30, 228, 179), align='center')
    used_height = y + text_height
    # ~~~~~~~~~~ end Text: name text ~~~~~~~~~~~~

    # ~~~~~~~~~~ Text: badge text ~~~~~~~~~~~~
    # Add text to the container using the ImageDraw module
    draw = ImageDraw.Draw(container)
    text = f"ROBIN {badge_text.upper()}"
    font = ImageFont.truetype(urlopen(font_family_url), 30)
    # get text box size
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = (
                                      text_box[2] - text_box[0]), (text_box[3] - text_box[1])
    x = (container.width - text_width) / 2
    y = int(used_height + margin*0.5)
    draw.text((x, y), text, font=font, fill=(30, 228, 179), align='center')
    used_height = y + text_height
    # ~~~~~~~~~~ end Text: badge text ~~~~~~~~~~~~

    # ~~~~~~~~~~ Text: drive_count text ~~~~~~~~~~~~
    draw = ImageDraw.Draw(container)
    drive_count_decorated = get_count_decorated(drive_count)
    text = f"I just checked-in to my \n {drive_count_decorated} drive with RHA!"
    font = ImageFont.truetype(urlopen(font_family_url), 60)
    # get text box size
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = (
        text_box[2] - text_box[0]), (text_box[3] - text_box[1])
    x = (container.width - text_width) / 2
    y = int(used_height + margin)
    draw.text((x, y), text, font=font, fill=(255, 255, 255), align='center')
    used_height = y + text_height
    # ~~~~~~~~~~ end Text: drive_count text ~~~~~~~~~~~~

    # ~~~~~~ url box ~~~~~~
    rha_url_response = requests.get('https://checkin.robinhoodarmy.com/assets/robinhood/banner/website-url.png' )
    rha_url_img = Image.open(io.BytesIO(rha_url_response.content))
    # resize the url image
    new_size = tuple(dim - padding-margin for dim in container_size)
    rha_url_img.thumbnail(new_size)

    # paste the url image in the center of the container
    url_width, url_height = rha_url_img.size
    x = (container_width - url_width) // 2
    y = int(used_height + margin*1.5)
    container.paste(rha_url_img, (x, y))
    used_height = y + url_height
    # ~~~~~~ end: url box ~~~~~~
    
    container_byte_arr = io.BytesIO()
    container.save(container_byte_arr, format='JPEG')
    # container_byte_arr.seek(0)
    # return the image as a response
    # return send_file(container_byte_arr, mimetype='image/jpeg')

    frappe.response.filename = 'MyLatestCheckin.jpg'
    frappe.response.filecontent = container_byte_arr.getvalue()
    frappe.response.type = "download"
    frappe.response.display_content_as = "inline"

# create_gradient_image
def create_gradient_image(container_size, color1, color2):
    # get the size of the gradient image
    width, height = container_size

    # Create a new image with a white background
    gradient_image = Image.new('RGB', (width, height), color=(255, 255, 255))

    # Create a draw object for the image
    draw = ImageDraw.Draw(gradient_image)

    # Draw the vertical gradient on the image
    for y in range(height):
        # Calculate the color for this row
        r = int(color1[0] + (y / (height - 1)) * (color2[0] - color1[0]))
        g = int(color1[1] + (y / (height - 1)) * (color2[1] - color1[1]))
        b = int(color1[2] + (y / (height - 1)) * (color2[2] - color1[2]))
        color = (r, g, b)
        # Draw a line for this row with the calculated color
        draw.line((0, y, width, y), fill=color)

    # Save the gradient image
    # gradient_image.save('gradient_image.png')

    return gradient_image


# put_border_radius
def put_border_radius(image, border_radius, border_width=5, border_color=(255, 255, 255)):
    # create a new image
    img_container_size = (image.width, image.height)
    img_container = Image.new('RGBA', img_container_size, (0, 0, 0, 0))
    mask = Image.new("L", img_container_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0)+img_container_size,
                           radius=border_radius, fill=255, outline=255, width=border_width)

    # paste the image onto the img_container using the mask
    img_container.paste(image, (0, 0))
    img_container.putalpha(mask)

    # Draw the border
    draw = ImageDraw.Draw(img_container)
    draw.rounded_rectangle((0, 0) + img_container_size,
                           radius=border_radius, outline=border_color, width=border_width)

    return img_container


# get_badge_details
def get_badge_details(drive_count):
    badge_text = ""
    badge_img_path = ""
    if(drive_count >= 100):
        badge_text = "centurion"
        badge_img_path = "centurion"
    elif(drive_count >= 50):
        badge_text = "gladiator"
        badge_img_path = "gladiator"
    elif(drive_count >= 10):
        badge_text = "ninja"
        badge_img_path = "ninja"
    elif(drive_count >= 0):
        badge_text = "cadet"
        badge_img_path = "cadet"

    return badge_text, badge_img_path


# get_count_decorated
def get_count_decorated(drive_count):
    count_decorated = ""
    if(drive_count%10 == 1 and drive_count%100 != 11):
        count_decorated = f"{drive_count}ˢᵗ"
    elif(drive_count%10 == 2 and drive_count%100 != 12):
        count_decorated = f"{drive_count}ⁿᵈ"
    elif(drive_count%10 == 3 and drive_count%100 != 13):
        count_decorated = f"{drive_count}ʳᵈ"
    else:
        count_decorated = f"{drive_count}ᵗʰ"

    return count_decorated
