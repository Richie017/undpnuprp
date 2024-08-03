class ColorCode(object):
    @staticmethod
    def get_spaced_colors(n):
        """
        :param n: total number of color codes that will be generated
        :return: generated color code list
        """
        max_value = 16581375  # 255*225*225
        space = 76
        interval = int(max_value / space)
        # colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]
        colors = ['00a99d', '2e3192', 'da1c5c', 'b61291', 'f6b80c', '000000',
                  '00dbc6', '4a5cdd', 'ffa4c9', '666666', 'b3b3b3', 'ffffff',
                  'ff0000', '00ff00', '0000ff']
        import copy
        colors_list = copy.deepcopy(colors)
        if n > len(colors):
            for i in range(len(colors), n):
                colors_list += [colors[i % len(colors)]]
        return colors_list[:n]

    #  dgreen,dblue, dred, dpurple, dyellow, dblack,
    #  lgreen, lblue, lred, lblack, lwhite, dwhite
    #  red, green, blue

    # '00a99d'-dark green
    # '00dbc6'-light green
    # '2e3192'-dark blue
    # '4a5cdd'-light blue
    # 'da1c5c'-dark red
    # 'ffa4c9'-light red
    # 'b61291'-dark shed of purple
    # 'f6b80c'-dark shed of yellow
    # '000000'-dark black
    # '666666'-light shed of black
    # 'ff0000'-Red
    # '00ff00'-Green
    # '0000ff'-Blue
    # 'ffffff'-dark white
    # 'b3b3b3'-light shed of white(light ash)

    @staticmethod
    def get_color_code(c):
        colors = {
            "dark green": '00a99d',
            'brown': 'A52A2A',
            "light green": '00dbc6',
            "dark blue": '2e3192',
            "light blue": '4a5cdd',
            "dark red": 'da1c5c',
            "light red": 'ffa4c9',
            "purple": 'b61291',
            "yellow": 'f6b80c',
            "dark black": '000000',
            "shed black": '666666',
            "red": 'ff0000',
            "green": '00A99d',
            "blue": '5b6dee',
            "dark white": 'ffffff',
            "light ash": 'b3b3b3',
            "grey": '595c60',
            "lush": '56ab2f',
            "magenta": 'ff00ff',
            "maroon": '800000',
            "olive": '808000',
            "orange": 'ffa500',
            "orchid": 'da70d6',
            "sienna": 'a0522d',
            "turquoise": '40e0d0',
            "azure": '007fff'
        }
        color_list = list()
        for name in c:
            for key, c_name in colors.items():
                if key == name:
                    color_list.append(c_name)
                    break
        return color_list
