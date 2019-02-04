# This code provides a very simple implementation of the maze and how the maze's walls can be printed visually.
# You may use this as a starting point or develop your own maze implementation.

class Cell:
	def __init__(self, west, north, east, south, visited = False):
		# There are 4 walls per cell
		# Wall values can be 'W', 'O', or '?' (wall, open, or unknown)
		self.west = west
		self.north = north
		self.east = east
		self.south = south
		
		# Store whether or not the cell has been visited before
		self.visited = visited

		
# Helper function that verifies all the walls of the maze
def detectMazeInconsistencies(maze):
	# Check horizontal walls
	for i in range(3):
		for j in range(4):
			pos1 = i * 4 + j
			pos2 = i * 4 + j + 4
			hWall1 = maze[pos1].south
			hWall2 = maze[pos2].north		
			assert hWall1 == hWall2, " Cell " + str(pos1) + "'s south wall doesn't equal cell " + str(pos2) + "'s north wall! ('" + str(hWall1) + "' != '" + str(hWall2) + "')"
	
	# Check vertical walls
	for i in range(4):
		for j in range(3):
			pos1 = i * 4 + j
			pos2 = i * 4 + j + 1
			vWall1 = maze[pos1].east
			vWall2 = maze[pos2].west
			assert vWall1 == vWall2, " Cell " + str(pos1) + "'s east wall doesn't equal cell " + str(pos2) + "'s west wall! ('" + str(vWall1) + "' != '" + str(vWall2) + "')"

			
# You don't have to understand how this function works
def printMaze(maze, hRes = 4, vRes = 2):
	assert hRes > 0, "Invalid horizontal resolution"
	assert vRes > 0, "Invalid vertical resolution"

	# Get the dimensions of the maze drawing
	hChars = 4 * (hRes + 1) + 2
	vChars = 4 * (vRes + 1) + 1
	
	# Store drawing into a list
	output = [" "] * (hChars * vChars - 1)
	
	# Draw top border
	for i in range(1, hChars - 2):
		output[i] = "_"
	
	# Draw bottom border
	for i in range(hChars * (vChars - 1) + 1, hChars * (vChars - 1) + hChars - 2):
		output[i] = "¯"
	
	# Draw left border
	for i in range(hChars, hChars * (vChars - 1), hChars):
		output[i] = "|"
		
	# Draw right border
	for i in range(2 * hChars - 2, hChars * (vChars - 1), hChars):
		output[i] = "|"

	# Draw newline characters
	for i in range(hChars - 1, hChars * vChars - 1, hChars):
		output[i] = "\n"
	
	# Draw dots inside maze
	for i in range((vRes + 1) * hChars, hChars * (vChars - 1), (vRes + 1) * hChars):
		for j in range(hRes + 1, hChars - 2, hRes + 1):
			output[i + j] = "·"
	
	# Draw question marks if cell is unvisited
	for i in range(4):
		for j in range(4):
			cellNum = i * 4 + j
			if maze[cellNum].visited:
				continue
			origin = (i * hChars * (vRes + 1) + hChars + 1) + (j * (hRes + 1))
			for k in range(vRes):
				for l in range(hRes):
					output[origin + k * hChars + l] = "?"
	
	# Draw horizontal walls
	for i in range(3):
		for j in range(4):
			cellNum = i * 4 + j
			origin = ((i + 1) * hChars * (vRes + 1) + 1) + (j * (hRes + 1))
			hWall = maze[cellNum].south
			for k in range(hRes):
				output[origin + k] = "-" if hWall == 'W' else " " if hWall == 'O' else "?"
	
	# Draw vertical walls
	for i in range(4):
		for j in range(3):
			cellNum = i * 4 + j
			origin = hChars + (hRes + 1) * (j + 1) + i * hChars * (vRes + 1)
			vWall = maze[cellNum].east
			for k in range(vRes):
				output[origin + k * hChars] = "|" if vWall == 'W' else " " if vWall == 'O' else "?"

	# Print drawing
	print(''.join(output))


# Initialize the maze with a set of walls and visited cells
# The bottom right cell is marked as unvisited and with unknown walls
maze = [
	Cell('W','W','O','O', True), Cell('O','W','O','O', True), Cell('O','W','O','O', True), Cell('O','W','W','O', True),
	Cell('W','O','W','O', True), Cell('W','O','W','W', True), Cell('W','O','W','O', True), Cell('W','O','W','O', True),
	Cell('W','O','W','O', True), Cell('W','W','W','O', True), Cell('W','O','W','O', True), Cell('W','O','W','?', True),
	Cell('W','O','O','W', True), Cell('O','O','O','W', True), Cell('O','O','?','W', True), Cell('?','?','W','W', False)
]	

# How to modify a cell
#maze[0].east = 'W'
#maze[0].visited = False

detectMazeInconsistencies(maze)
printMaze(maze)