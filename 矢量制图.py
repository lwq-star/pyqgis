"""创建一个新的打印布局"""
project = QgsProject.instance()             # 返回项目实例
manager = project.layoutManager()           # 返回项目的布局管理器
layoutName = "PrintLayout"

# 如果已有相同名称的布局则移除
layouts_list = manager.printLayouts()       # 返回管理器中包含的所有打印布局的列表
for layout in layouts_list:
    if layout.name() == layoutName:
        manager.removeLayout(layout)

layout = QgsPrintLayout(project)            # 创建一个新的打印布局对象，将 QgsProject 作为参数
layout.initializeDefaults()                 # 创建默认地图画布
pc = layout.pageCollection()
# QgsLayoutItemPage.Orientation.Landscape\Portrait 为横向\纵向
pc.pages()[0].setPageSize('A4', QgsLayoutItemPage.Orientation.Landscape)
layout.setName(layoutName)
manager.addLayout(layout)                   # 向管理器添加布局


"""将地图项添加到打印布局"""
map = QgsLayoutItemMap(layout)              # 定义一个地图布局项
map.setRect(20, 20, 20, 20)                 # 设置一个矩形框架
# 设置范围
#rectangle = QgsRectangle(1355502, -46398, 1734534, 137094)  # 一个关于如何用坐标设置地图范围的例子
#map.setExtent(rectangle)
canvas = iface.mapCanvas()
map.setExtent(canvas.extent())               # 将地图范围设置为当前地图画布
layout.addLayoutItem(map)                    # 将项目添加到布局
#Move & Resize
# 将地图移动到一个位置（x,y）地图布局坐标使用屏幕坐标，原点在页面的左上方，最大坐标在页面的右下方。
map.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutMillimeters))  # 尝试将项目移动到指定点
# 尝试将项目的大小调整为指定的目标大小,单位为毫米
map.attemptResize(QgsLayoutSize(297, 210, QgsUnitTypes.LayoutMillimeters))
# map.setScale(133275728)

"""收集活动图层以添加到图例中"""
# 检查图层树对象并将其存储在一个列表中。这包括csv表
checked_layers = [layer.name() for layer in QgsProject().instance().layerTreeRoot().children() if layer.isVisible()]
print(f"Adding {checked_layers} to legend." )
# 通过匹配其名称来获取选中图层的地图图层对象并将其存储在列表中
layersToAdd = [layer for layer in QgsProject().instance().mapLayers().values() if layer.name() in checked_layers]
root = QgsLayerTree()
for layer in layersToAdd:
    # 将图层对象添加到图层树
    root.addLayer(layer)


"""在 "打印布局 "中添加一个图例项目"""
legend = QgsLayoutItemLegend(layout)
legend.model().setRootGroup(root)
layout.addLayoutItem(legend)
legend.attemptMove(QgsLayoutPoint(20,185, QgsUnitTypes.LayoutMillimeters))

"""将标签添加到地图"""
title = QgsLayoutItemLabel(layout)
title.setText("Title Here")
title.setFont(QFont("Arial", 28))     # 设置标签的当前字体
title.adjustSizeToText()              # 调整项目的大小，使标签的文字适合于项目。保持左上角不动
layout.addLayoutItem(title)
title.attemptMove(QgsLayoutPoint(10, 4, QgsUnitTypes.LayoutMillimeters))

subtitle = QgsLayoutItemLabel(layout)
subtitle.setText("Subtitle Here")
subtitle.setFont(QFont("Arial", 17))
subtitle.adjustSizeToText()
layout.addLayoutItem(subtitle)
subtitle.attemptMove(QgsLayoutPoint(11, 20, QgsUnitTypes.LayoutMillimeters))  # 允许移动文本框

# credit_text = QgsLayoutItemLabel(layout)
# credit_text.setText("Credit Text Here")
# credit_text.setFont(QFont("Arial", 10))
# credit_text.adjustSizeToText()
#layout.addLayoutItem(credit_text)
#credit_text.attemptMove(QgsLayoutPoint(246, 190, QgsUnitTypes.LayoutMillimeters))

"""将比例尺添加到布局中"""
bar = QgsLayoutItemScaleBar(layout)
bar.setStyle('Line Ticks Up') # 可以选择修改样式
bar.setUnits(QgsUnitTypes.DistanceKilometers)   # 设置比例尺使用的距离单位
bar.setNumberOfSegments(2)      # 设置比例尺的段数
bar.setNumberOfSegmentsLeft(0)  # 设置原点左侧的比例尺段数
bar.setUnitsPerSegment(100)     # 设置每段比例尺的距离
bar.setLinkedMap(map)           # 设置链接到比例尺的地图项
bar.setUnitLabel('千米')         # 设置单位的标签
bar.setFont(QFont('Arial', 14))  # 设置用于在比例尺中绘制文本的字体
bar.update()                     # 调整比例尺框大小并更新项目
layout.addLayoutItem(bar)
bar.attemptMove(QgsLayoutPoint(210, 190, QgsUnitTypes.LayoutMillimeters))

"""添加指北针"""
north=QgsLayoutItemPicture(layout)
north.setMode(QgsLayoutItemPicture.FormatSVG)    # 设置当前图像模式（图像格式）
svgpath = QgsApplication.svgPaths()[0] + "arrows/NorthArrow_04.svg"  # 返回svg目录的路径
north.setPicturePath(svgpath)      # 设置图像的源路径
north.attemptMove(QgsLayoutPoint(258, 12, QgsUnitTypes.LayoutMillimeters))
north.attemptResize(QgsLayoutSize(*[400,400], QgsUnitTypes.LayoutPixels))
layout.addLayoutItem(north)

"""添加经纬网"""
map = QgsLayoutItemMap(layout)
referenceMap = layout.referenceMap()
# We supposed you set a grid manually here
firstGrid = referenceMap.grid()
newGrid = QgsLayoutItemMapGrid ('My new grid', referenceMap)
map.grids().addGrid(newGrid)
firstGrid.setEnabled(True)
firstGrid.setIntervalX(1)
firstGrid.setIntervalY(1)
firstGrid.setAnnotationEnabled(True)


"""将打印布局导出为图像"""
manager = QgsProject.instance().layoutManager()  # 这是一个对布局管理器的引用，它包含一个打印布局的列表
#for layout in manager.printLayouts():           # 这将在一个列表中打印出所有现有的打印布局
#    print(layout.name())

layout = manager.layoutByName(layoutName)        # 这通过名称访问特定布局（这是一个字符串）

exporter = QgsLayoutExporter(layout)             # 这将创建一个 QgsLayoutExporter 对象
# exporter.exportToPdf(r'D:/QGIS-project/TestLayout.pdf', QgsLayoutExporter.PdfExportSettings())  # 这会导出布局对象的 pdf
# exporter.exportToImage(r'D:/QGIS-project/TestLayout.png', QgsLayoutExporter.ImageExportSettings())  # 这会导出布局对象的图像