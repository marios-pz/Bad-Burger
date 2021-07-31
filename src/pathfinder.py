from copy import copy


class VarContainer:
    first_pos: list
    second_pos: list
    grid: list


def init_pathfinder(first_pos, second_pos, grid):

    VarContainer.first_pos = first_pos
    VarContainer.second_pos = second_pos
    VarContainer.grid = grid

    found = find_path(VarContainer.first_pos)
    if found[0]:
        return found[1]
    return False
    

def find_path(pos):

    points = [pos]
    paths = [[pos]]
    while len(points) > 0:
        
        added = False
        
        new_paths = []
        for l_pts in paths:

            pt = l_pts[-1]
            pts = [
                [pt[0]+1, pt[1]],
                [pt[0]-1, pt[1]],
                [pt[0], pt[1]+1],
                [pt[0], pt[1]-1]
            ]
            for pt_ in pts:
                if pt_available(pt_) and pt_ not in points:
                    added = True
                    new = copy(l_pts)
                    points.append(pt_)
                    new.append(pt_)
                    new_paths.append(new)

        paths = new_paths
            
        for pts in paths:
            if VarContainer.second_pos in pts:
                return True, pts

        if not added:
            break
            
    return False, None

def pt_available(pos):
    grid = VarContainer.grid
    if pos[0] > len(grid[0])-1 or pos[1] > len(grid)-1 or pos[0] < 0 or pos[1] < 0:
        return False
    if grid[pos[1]][pos[0]] == 1:
        return False
    return True
