import pandas
import arcade
import numpy
import sys
import random
import math
import time

class Sample(arcade.Window):
    def __init__(self, width, height, data):
        super().__init__(width, height, 'k-mean')
        
        print(sys.argv[1])
        self._d = data
        self._values = []
        self._x_col = sys.argv[1]
        self._y_col = sys.argv[2]
        self._screen_w = width
        self._screen_h = height

        self._line = None
        self._circles = None
        self._point_index = 0
        self._cluster_points = []
        colors = [
                    arcade.color.BRIGHT_NAVY_BLUE,
                    arcade.color.BRICK_RED,
                    arcade.color.BRIGHT_GREEN,
                    arcade.color.DARK_ORANGE,
                    arcade.color.DARK_VIOLET
                ]

        index = 0
        while(index < int(sys.argv[3])) :
            self._cluster_points.append([random.randint(5, width - 5), random.randint(5, height - 5), colors[index]])
            index += 1

        self._next_update = 0

        arcade.set_background_color(arcade.color.WHITE)
        
    def setup(self):

        x_min_v = 0
        x_max_v = 0
        y_min_v = 0
        y_max_v = 0

        x_v = 0
        y_v = 0

        for i, row in self._d.iterrows():
            v = row[self._x_col]
            if v < x_min_v :
                x_min_v = v
            elif v > x_max_v :
                x_max_v = v

            v = row[self._y_col]
            if v < y_min_v :
                y_min_v = v
            elif v > y_max_v :
                y_max_v = v

        print("MAX " + str(x_max_v )+ ", MIN " + str(x_min_v))
        print("MAX " + str(y_max_v )+ ", MIN " + str(y_min_v))
        
        for i, row in self._d.iterrows():
             x_v = (row[self._x_col]/x_max_v) * (self._screen_w - 10) + 5
             y_v = (row[self._y_col]/y_max_v) * (self._screen_h - 10) + 5

             try :
                 x_v = int(x_v) 
             except:
                 pass

             try :
                 y_v = int(y_v) 
             except:
                 pass

             self._values.append([x_v, y_v, arcade.color.DARK_GRAY, None])
    
    def on_draw(self):
        """ Render the screen """
        arcade.start_render()

        for a in self._values :
            arcade.draw_point(a[0], a[1], a[2], 5)
        
        for c in self._cluster_points :
            arcade.draw_circle_filled(c[0], c[1], 5, c[2])

        if self._line is not None:
            start_x = self._values[self._line[0]][0]
            start_y = self._values[self._line[0]][1]
            end_x = self._cluster_points[self._line[1]][0]
            end_y = self._cluster_points[self._line[1]][1]
            color = self._cluster_points[self._line[1]][2]

            arcade.draw_line(start_x, start_y, end_x, end_y, color, 1)

        if self._circles is not None:
            for c in self._circles :
                arcade.draw_circle_outline(c[0], c[1], c[2], c[3], 1)
        arcade.finish_render()

    def update(self, arg1):
        """ Updates """
        millis = int(round(time.time() * 1000))

        if millis > self._next_update :
            if self._point_index == len(self._values):
                self._point_index = -1
                self._line = None
            elif self._point_index >= 0 and self._point_index < len(self._values) :
                min_distance = 999999
                closest_cluster = None
                index = 0
                while(index < len(self._cluster_points)):
                    c = self._cluster_points[index]
                    start_x = self._values[self._point_index][0]
                    start_y = self._values[self._point_index][1]
                    end_x = c[0]
                    end_y = c[1]
                    delta_x = math.fabs(end_x - start_x)**2
                    delta_y = math.fabs(end_y - start_y)**2
                    distance = math.sqrt(delta_x + delta_y)

                    if distance < min_distance:
                        min_distance = distance
                        closest_cluster = index
                        self._values[self._point_index][2] = c[2]
                        self._values[self._point_index][3] = index
                    index += 1

                self._line = [self._point_index, closest_cluster]
                self._point_index += 1
            elif self._point_index == -1 :
                index = 0
                is_there_change = False
                while index < len(self._cluster_points) :
                    sum_x = 0
                    sum_y = 0
                    count = 0
                    for p in self._values:
                        if p[3] == index :
                            sum_x += p[0]
                            sum_y += p[1]
                            count += 1

                    if count == 0 :
                        c_x = self._cluster_points[index][0]
                        c_y = self._cluster_points[index][1]
                    else :
                        c_x = int(sum_x/count)
                        c_y = int(sum_y/count)
                   
                    print("New centroid " + str(index) + " - " + str(c_x) + ", " + str(c_y))
                    if c_x != self._cluster_points[index][0]:
                        self._cluster_points[index][0] = c_x
                        is_there_change = True
                    
                    if c_y != self._cluster_points[index][1]:
                        self._cluster_points[index][1] = c_y
                        is_there_change = True

                    index += 1

                if is_there_change :
                    self._point_index = 0
                else :
                    self._circles = []
                    index = 0
                    while(index < len(self._cluster_points)):
                        c = self._cluster_points[index]
                        max_distance = 0
                        end_x = c[0]
                        end_y = c[1]

                        for v in self._values :
                            distance = 0
                            if v[3] == index :
                                start_x = v[0]
                                start_y = v[1]
                                delta_x = math.fabs(end_x - start_x)**2
                                delta_y = math.fabs(end_y - start_y)**2
                                distance = math.sqrt(delta_x + delta_y)

                            if distance > max_distance:
                                max_distance = distance
                        
                        self._circles.append([end_x, end_y, int(max_distance), c[2]])
                        index += 1


            self._next_update = 1000 + int(round(time.time() * 1000))

def main():
    v = pandas.read_csv('data.csv', sep=';')
    v = v.drop_duplicates('ID')

    sample = Sample(700, 500, v)
    sample.setup()
    arcade.run()


if __name__ == '__main__' :
    main()
