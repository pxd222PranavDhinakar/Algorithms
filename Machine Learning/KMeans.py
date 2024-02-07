from manim import *
from manim.opengl import *
import random
import colorsys
 

class KMeansClustering(Scene):
    numOfClusters = 3
    numOfPointsPerCluster = 20
    maxIterations = 5
 
    def construct(self):
        heading = Text("K Means Clustering", font_size=35).to_edge(UP)
 
        axis = Axes(
            x_range=[-5, 5],
            y_range=[-5, 5],
            x_length=5,
            y_length=5,
            axis_config={"include_ticks": False},
            tips=False,
        ).shift(DOWN * 0.75)
 
        clusters = VGroup()
 
        allGroup = VGroup(heading, axis, clusters)
 
        for i in range(__class__.numOfClusters):
            cluster = self.generateRandomDots(
                [-5, 5],
                [-5, 5],
                __class__.numOfPointsPerCluster,
                axis,
                dotArgs={"radius": 0.08},
            )
            clusters.add(cluster)
 
        self.play(Create(allGroup))
 
        self.wait()
 
        # Initialize Clusters
        clusterColors = self.generateClusterColors()
        for cluster, clusterColor in zip(clusters, clusterColors):
            self.play(cluster.animate.set_color(clusterColor), run_time=1)
 
        # Create Cluster Centers
        clusterCenterDots = Group()
        for cluster, clusterColor in zip(clusters, clusterColors):
            clusterCenter = cluster.get_center_of_mass()
            clusterCenterDots.add(
                Dot(clusterCenter, radius=0.2, fill_opacity=0.75, color=clusterColor)
            )
        self.play(FadeIn(clusterCenterDots))
 
        # Create Cluster Labels
        clusterLabels = VGroup()
        for clusterCount, clusterColor in enumerate(clusterColors):
            clusterLabel = Tex(
                f"Cluster {clusterCount+1}", color=clusterColor, font_size=30
            )
            clusterLabels.add(clusterLabel)
        clusterLabels.arrange(DOWN, buff=0.5).to_corner(DL, buff=0.25)
 
        self.play(FadeIn(clusterLabels))
 
        self.wait(2)
 
        dotToClusterLine = Line()
        self.add(dotToClusterLine)
 
        # Recalculate Means and Assign Datapoints
        maxIterations = __class__.maxIterations
        while maxIterations != 0:
            for currentClusterIndex, cluster in enumerate(clusters):
                for i, dot in enumerate(cluster):
                    clusterMeans = self.getClusterMeans(clusters)
                    minDistanceClusterIndex = self.getLeastDistanceClusterIndex(
                        dot, clusterMeans
                    )
 
                    self.updateClusterCenterDots(clusterCenterDots, clusterMeans)
                    self.updateDotToClusterLine(
                        dotToClusterLine, dot, clusterMeans[minDistanceClusterIndex]
                    )
                    self.wait(0.5)
                    if currentClusterIndex == minDistanceClusterIndex:
                        continue
                    else:
                        clusters[minDistanceClusterIndex].add(dot)
                        clusters[currentClusterIndex].remove(dot)
                        self.setClusterColor(clusters, clusterColors)
                        self.play(
                            Flash(dot, color=clusterColors[minDistanceClusterIndex]),
                            run_time=1,
                        )
            maxIterations -= 1
 
        self.wait(1)
        self.interactive_embed()
 
    def generateRandomDots(
        self,
        xRange: list,
        yRange: list,
        numOfDots: int,
        axis: Axes = None,
        dotArgs: dict = None,
    ) -> VGroup:
        dotsVGroup = VGroup()
 
        if dotArgs is None:
            dotArgs = {}
 
        for i in range(numOfDots):
            xCoord = round(random.uniform(*xRange), 2)
            yCoord = round(random.uniform(*yRange), 2)
 
            finalCoord = [
                xCoord,
                yCoord,
                0,
            ]  # manim requires the center of Dot to be 3D Point
            if axis:
                finalCoord = axis.c2p(*finalCoord)
 
            dotsVGroup.add(Dot(finalCoord, **dotArgs))
        return dotsVGroup
 
    @staticmethod
    def generateClusterColors() -> list:
        clusterColors = []
        for i in range(1, __class__.numOfClusters + 1):
            h = (1 / __class__.numOfClusters) * float(i)
            l = 0.6
            s = 0.6
            clusterColors += [ManimColor(colorsys.hls_to_rgb(h, l, s))]
 
        return clusterColors
 
    def setClusterColor(self, clusters: VGroup, clusterColors: list) -> None:
        for cluster, clusterColor in zip(clusters, clusterColors):
            cluster.set_color(clusterColor)
 
    def getClusterMeans(self, clusters: VGroup) -> list:
        return [cluster.get_center_of_mass() for cluster in clusters]
 
    def getLeastDistanceClusterIndex(self, dot: Dot, clusterMeans: list) -> int:
        distances = []
        x1 = dot.get_x()
        y1 = dot.get_y()
        for mean in clusterMeans:
            x2 = mean[0]
            y2 = mean[1]
 
            distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (1 / 2)
            distances += [distance]
 
        return distances.index(min(distances))
 
    def updateClusterCenterDots(
        self, clusterCenterDots: Group, clusterMeans: list
    ) -> None:
        for idx, mean in enumerate(clusterMeans):
            clusterCenterDots[idx].move_to(mean)
 
    def updateDotToClusterLine(
        self, dotToClusterLine: Line, dot: Dot, clusterMean
    ) -> None:
        start = dot.get_center()
        end = clusterMean
        dotToClusterLine.put_start_and_end_on(start, end)
 

class KMeansPlusPlus(Scene):
    # Random Number Generator
    rng = random.seed(10)
 
    numOfClusters = 4
    numOfPointsPerCluster = 20
 
    # Max Iterations of Clustering Algorithm
    maxIterations = 5
 
    # Spread of Points of Clusters
    # Values less than 1 give concentrated clusters
    spreadOfPoints = 0.8
 
    # Scales the probability Lines for a better view
    probabilityScaleFactor = int((numOfPointsPerCluster * numOfClusters) / 3)
 
    def construct(self):
        axis = (
            Axes(
                x_range=[0, 8],
                y_range=[0, 4],
                x_length=8,
                y_length=4,
                tips=False,
            )
            .to_corner(UR, buff=1)
            .shift(UP * 0.5)
        )
 
        totalNumOfPoints = __class__.numOfClusters * __class__.numOfPointsPerCluster
        if totalNumOfPoints <= 500:
            probabilityAxis = Axes(
                x_range=[0, totalNumOfPoints],
                y_range=[0, 1],
                x_length=axis.x_length,
                y_length=2,
                tips=False,
                x_axis_config={
                    "include_ticks": False,
                    "include_numbers": False,
                    "font_size": 10,
                },
            ).next_to(axis, DOWN, buff=0.4)
            probabilityAxis.y_axis.add_labels(
                {0: MathTex(0), 0.5: MathTex("P(x)"), 1: MathTex(1)},
                font_size=20,
            )
        else:
            raise ValueError(
                f"Total number of points ({totalNumOfPoints}) is greater than 500"
            )
 
        clusterDots = self.generateRandomDots(
            axis.x_range[:-1],  # remove step value from x_range
            axis.y_range[:-1],
            100,
            axis,
            {"radius": 0.05},
        ).set_z_index(5)
 
        clusterCenters = VGroup()
        # Initialize first cluster center
        clusterCenters.selectedDot = random.choice(clusterDots)
        clusterColors = self.generateClusterColors()
 
        firstStep = (
            Paragraph(
                "1. The first step is initialization",
                "\nwhere a point from dataset",
                "\nis picked randomly.",
                line_spacing=-0.1,
                height=1.1,
            )
            .to_corner(UL, buff=0.3)
            .shift(DOWN * 0.5)
        )
        secondStep = (
            Paragraph(
                "2. Choose a cluster center",
                "\nprobabilistically using",
                "\nscore given to each point",
                line_spacing=-0.1,
                height=1.1,
            )
            .next_to(firstStep, DOWN, buff=1)
            .shift(LEFT * 0.4)
        )
        thirdStep = (
            Paragraph(
                "3. Repeat step 2 until",
                "\nk means are selected.",
                line_spacing=-0.1,
                height=0.65,
            )
            .next_to(secondStep, DOWN, buff=1)
            .shift(LEFT * 0.3)
        )
 
        self.add(firstStep, secondStep, thirdStep)
 
        self.play(
            *[Create(item) for item in [axis, probabilityAxis, clusterDots]],
            lag_ratio=0.5,
        )
 
        for i in range(__class__.numOfClusters):
            if i == 0:
                self.play(self.selectClusterAnimation(clusterCenters, clusterColors))
                self.wait(1)
                self.play(Indicate(firstStep))
 
            self.setClosestClusterPointsAndLines(clusterCenters, clusterDots)
 
            if i != __class__.numOfClusters - 1:
                self.play(self.drawLinesAnimation(clusterCenters))
                self.play(
                    self.drawProbabilityLinesAnimation(probabilityAxis, clusterCenters)
                )
                self.play(self.selectLineAnimation(clusterCenters), run_time=3)
                self.play(
                    Indicate(secondStep),
                    self.selectClusterAnimation(clusterCenters, clusterColors),
                    run_time=2,
                )
 
            if i == 1:
                self.play(Indicate(thirdStep))
 
            self.play(self.getRemoveLinesAnimation(clusterCenters))
 
    def selectClusterAnimation(self, clusterCenters: VGroup, clusterColors):
        newCluster = (
            clusterCenters.selectedDot.copy()
            .scale(2)
            .set_opacity(0.7)
            .set_color(self.getClusterColor(clusterColors))
        )
        clusterCenters.add(newCluster)
 
        return Indicate(newCluster, 2, color=newCluster.get_color())
 
    @staticmethod
    def generateRandomDots(
        xRange, yRange, numOfPoints, axis=None, dotArgs=None
    ) -> VGroup:
        """
        Parameters:
        xRange : X-Axis range in which points should lie
        yRange : Y-Axis range in which points should lie
        numOfPoints : Total number of points to be generated
        dotArgs : Arguments passed on to each individual points/Dot(s)
 
        returns:
        dots : VGroup of all the dots/points generated
        """
        if dotArgs == None:
            dotArgs = {}
 
        dots = VGroup()
 
        # Function which generates the coordinates of the points,
        # within a range using gaussian sampling
        def genPoint(mu, sigma, point, pointRange):
            if point > max(pointRange) or point < min(pointRange):
                point = random.gauss(mu, sigma)
                return genPoint(mu, sigma, point, pointRange)
            else:
                return point
 
        sigma = __class__.spreadOfPoints
        for i in range(__class__.numOfClusters):
            mu_x = random.uniform(*xRange)
            mu_y = random.uniform(*yRange)
 
            for j in range(__class__.numOfPointsPerCluster):
                # Passing xRange[1] + 1 in the place of point argument in genPoint makes it
                # so that the if condition in genPoint becomes True and a point
                # is generated
                xCoord = genPoint(mu_x, sigma, xRange[1] + 1, xRange)
                yCoord = genPoint(mu_y, sigma, yRange[1] + 1, yRange)
 
                finalCoord = (xCoord, yCoord, 0)
 
                if axis:
                    finalCoord = axis.c2p(*finalCoord)
 
                dots.add(Dot(finalCoord, **dotArgs))
        return dots
 
    @staticmethod
    def generateClusterColors() -> list[ManimColor]:
        """
        returns: A list of colors based on number of clusters
        """
        clusterColors = []
        for i in range(1, __class__.numOfClusters + 1):
            h = (1 / __class__.numOfClusters) * float(i)
            l = 0.6
            s = 0.8
            clusterColors += [ManimColor(colorsys.hls_to_rgb(h, l, s))]
 
        return clusterColors
 
    @staticmethod
    def getClusterColor(clusterColors: list) -> ManimColor:
        """
        It pops the value at the last index from clusterColors and
        returns the popped value
 
        Parameters:
        clusterColors : A list of cluster colors
 
        returns:
        ManimColor : A single ManimColor Object
        """
        return clusterColors.pop()
 
    @staticmethod
    def setClosestClusterPointsAndLines(
        clusterCenters: VGroup, clusterDots: VGroup, lineArgs=None
    ) -> dict:
        """
        Adds closestPointAndLines attribute to each cluster center in clusterCenters
            Example:
            clusterCenter.closestPoints -> [Dot , Dot , ...]
            clusterCenter.closestLines -> [Line , Line , ...]
 
        Parameters:
        clusterCenters : VGroup of all the cluster centers
        clusterDots: VGroup of all the dots
        lineArgs : Arguments passed onto the Line mobject
        """
        clusterCenters.totalLineLength = 0
 
        if lineArgs == None:
            lineArgs = {}
 
        for clusterCenter in clusterCenters:
            clusterCenter.closestPoints = []
            clusterCenter.closestLines = []
            clusterCenter.probabilityLines = []
            clusterCenter.originalLines = []
 
        for dot in clusterDots:
            dotDistanceFromClusters = []
            x2, y2 = dot.get_center()[:-1]  # get rid of z coord
 
            # Add distance of different clusters from the same
            # point to dotDistanceFromClusters
            for clusterCenter in clusterCenters:
                x1, y1 = clusterCenter.get_center()[:-1]
                distance = (x2 - x1) ** 2 + (y2 - y1) ** 2
                dotDistanceFromClusters.append(distance)
 
            minDistance = min(dotDistanceFromClusters)
 
            closestCluster = clusterCenters[dotDistanceFromClusters.index(minDistance)]
            line = Line(
                closestCluster.get_center(), dot.get_center(), **lineArgs
            ).set_color(closestCluster.get_color())
 
            clusterCenters.totalLineLength += line.get_length()
            closestCluster.closestPoints += [dot]
            closestCluster.closestLines += [line]
 
    @staticmethod
    def drawLinesAnimation(clusterCenters: VGroup) -> AnimationGroup:
        allAnimations = []
        for clusterCenter in clusterCenters:
            clusterAnimation = []
            for line in clusterCenter.closestLines:
                clusterAnimation += [Create(line)]
            allAnimations += [AnimationGroup(*clusterAnimation, lag_ratio=0.01)]
 
        return AnimationGroup(*allAnimations, lag_ratio=0.5)
 
    @staticmethod
    def drawProbabilityLinesAnimation(
        axis: Axes, clusterCenters: VGroup
    ) -> AnimationGroup:
        totalLineLength = clusterCenters.totalLineLength * axis.y_length
        allAnimations = []
        probabilityScaleFactor = __class__.probabilityScaleFactor
        count = 0
 
        for clusterCenter in clusterCenters:
            for line in clusterCenter.closestLines:
                normalizedLineLength = line.get_length() / (totalLineLength)
 
                # Ignore lines which have zero probability
                if normalizedLineLength == 0:
                    count += 1
                    continue
 
                start = axis.c2p(count + 1, 0, 0)
                end = axis.c2p(
                    count + 1, probabilityScaleFactor * normalizedLineLength, 0
                )
                originalLine = line.copy()
                normalizedLine = line.copy().put_start_and_end_on(start, end)
 
                clusterCenter.probabilityLines += [normalizedLine]
                clusterCenter.originalLines += [originalLine]
                allAnimations += [Transform(originalLine, normalizedLine)]
                count += 1
 
        return AnimationGroup(*allAnimations, lag_ratio=0.05)
 
    @staticmethod
    def selectLineAnimation(clusterCenters: VGroup):
        probabilityLines = []
        for clusterCenter in clusterCenters:
            probabilityLines += clusterCenter.probabilityLines
 
        # Select a line from top 10 all of probabilityLines with highest probabilities
        probabilityLines = sorted(
            probabilityLines,
            key=lambda line: line.get_length(),
            reverse=True,
        )[0:6]
 
        def dotInGroup(dot: Dot, clusterCenters):
            dotX = dot.get_x()
            dotY = dot.get_y()
            for clusterCenter in clusterCenters:
                clusterCenterX = clusterCenter.get_x()
                clusterCenterY = clusterCenter.get_y()
                if dotX == clusterCenterX and dotY == clusterCenterY:
                    return True
            return False
 
        def selectLine(clusterCenters, probabilityLines):
            selectedLine = random.choice(probabilityLines)
            for clusterCenter in clusterCenters:
                for i, line in enumerate(clusterCenter.probabilityLines):
                    if line == selectedLine:
                        if dotInGroup(clusterCenter.closestPoints[i], clusterCenters):
                            return selectLine(clusterCenters, probabilityLines)
            return selectedLine
 
        selectedProbabilityLine = selectLine(clusterCenters, probabilityLines)
 
        allAnimations = []
        for clusterCenter in clusterCenters:
            for i, probabilityLine in enumerate(clusterCenter.probabilityLines):
                if probabilityLine == selectedProbabilityLine:
                    graphLine = clusterCenter.closestLines[i]
                    graphDot = clusterCenter.closestPoints[i]
                    clusterCenters.selectedDot = graphDot
                else:
                    clusterCenter.closestLines[i].set_opacity(0.3)
 
        allAnimations += [Indicate(selectedProbabilityLine, 2)]
        allAnimations += [Indicate(graphLine, 2)]
        allAnimations += [Indicate(graphDot, 3)]
 
        return AnimationGroup(*allAnimations, lag_ratio=0.4)
 
    @staticmethod
    def getRemoveLinesAnimation(clusterCenters: VGroup):
        mobjectsToRemove = []
        for clusterCenter in clusterCenters:
            try:
                mobjectsToRemove += clusterCenter.closestLines
                mobjectsToRemove += clusterCenter.probabilityLines
                mobjectsToRemove += clusterCenter.originalLines
            except AttributeError:
                pass
 
        return AnimationGroup(
            *[Uncreate(item) for item in mobjectsToRemove], lag_ratio=0.01
        )