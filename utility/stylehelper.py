__author__ = 'kevin'

from PySide.QtCore import Qt, QPoint, QRect, QSize
from PySide.QtGui import qApp, QPalette, QColor, QApplication, \
    QLinearGradient, QPixmap, QPixmapCache, QPainter, QImage, \
    QPolygon, QStyle, QIcon, qGray, qRgba, qAlpha

from _utility__libspark_dev_ import config_ as config


def clamp(x):
    val = 255 if x > 255 else int(x)
    return 0 if val < 0 else val


class StyleHelper(object):
    DEFAULT_BASE_COLOR = 0x666666
    baseColor = QColor()
    requestedBaseColor = QColor()

    # Height of the project explorer navigation bar
    @staticmethod
    def navigationWidgetHeight():
        return 24

    @staticmethod
    def sidebarFontSize():
        if config.OS_MAC:
            return 10
        else:
            return 7.5

    @staticmethod
    def sidebarFontPalette(original):
        palette = original
        palette.setColor(QPalette.Active, QPalette.Text, StyleHelper.panelTextColor())
        palette.setColor(QPalette.Active, QPalette.WindowText, StyleHelper.panelTextColor())
        palette.setColor(QPalette.Inactive, QPalette.Text, StyleHelper.panelTextColor().darker())
        palette.setColor(QPalette.Inactive, QPalette.WindowText, StyleHelper.panelTextColor().darker())
        return palette

    @staticmethod
    def requestedBaseColor():
        return StyleHelper.requestedBaseColor

    @staticmethod
    def panelTextColor(lightColored=False):
        if not lightColored:
            return Qt.white
        else:
            return Qt.black

    @staticmethod
    def baseColor(lightColored):
        if not lightColored:
            return StyleHelper.baseColor
        else:
            return StyleHelper.baseColor.lighter(230)

    @staticmethod
    def highlightColor(lightColored):
        result = StyleHelper.baseColor(lightColored)
        if not lightColored:
            result.setHsv(result.hue(),
                          clamp(result.saturation()),
                          clamp(result.value() * 1.16))
        else:
            result.setHsv(result.hue(),
                          clamp(result.saturation()),
                          clamp(result.value() * 1.06))
        return result

    @staticmethod
    def shadowColor(lightColored):
        result = StyleHelper.baseColor(lightColored)
        result.setHsv(result.hue(),
                      clamp(result.saturation() * 1.1),
                      clamp(result.value() * 0.70))
        return result

    @staticmethod
    def borderColor(lightColored):
        result = StyleHelper.baseColor(lightColored)
        result.setHsv(result.hue(),
                      result.saturation(),
                      result.value() / 2)
        return result

    @staticmethod
    def buttonTextColor():
        return QColor(0x4c4c4c)

    @staticmethod
    def mergedColors(colorA, colorB, factor=50):
        maxFactor = 100
        tmp = colorA
        tmp.setRed((tmp.red() * factor) / maxFactor + (colorB.red() * (maxFactor - factor)) / maxFactor)
        tmp.setGreen((tmp.green() * factor) / maxFactor + (colorB.green() * (maxFactor - factor)) / maxFactor)
        tmp.setBlue((tmp.blue() * factor) / maxFactor + (colorB.blue() * (maxFactor - factor)) / maxFactor)
        return tmp

    @staticmethod
    def sidebarHighlight():
        return QColor(255, 255, 255, 40)

    @staticmethod
    def sidebarShadow():
        return QColor(0, 0, 0, 40)

    @staticmethod
    def setBaseColor(newcolor):
        StyleHelper.requestedBaseColor = newcolor
        color = QColor()
        color.setHsv(newcolor.hue(),
                     newcolor.saturation() * 0.7,
                     64 + newcolor.value() / 3)

        if color.isValid() and color != StyleHelper.baseColor:
            StyleHelper.baseColor = color
            for w in QApplication.topLevelWidgets():
                w.update()

    @staticmethod
    def verticalGradientHelper(p, spanRect, rect, lightColored):
        highlight = StyleHelper.highlightColor(lightColored)
        shadow = StyleHelper.shadowColor(lightColored)
        grad = QLinearGradient(spanRect.topRight(), spanRect.topLeft())
        grad.setColorAt(0, highlight.lighter(117))
        grad.setColorAt(1, shadow.darker(109))
        p.fillRect(rect, grad)

        light = QColor(255, 255, 255, 80)
        p.setPen(light)
        p.drawLine(rect.topRight() - QPoint(1, 0), rect.bottomRight() - QPoint(1, 0))
        dark = QColor(0, 0, 0, 90)
        p.setPen(dark)
        p.drawLine(rect.topLeft(), rect.bottomLeft())

    @staticmethod
    def verticalGradient(painter, spanRect, clipRect, lightColored):
        if StyleHelper.usePixmapCache():
            keyColor = StyleHelper.baseColor(lightColored)
            key = "mh_vertical {0} {1} {2} {3} {4}".format(spanRect.width(),
                                                           spanRect.height(),
                                                           clipRect.width(),
                                                           clipRect.height(),
                                                           keyColor.rgb())

            pixmap = QPixmap()
            if not QPixmapCache.find(key, pixmap):
                pixmap = QPixmap(clipRect.size())
                p = QPainter(pixmap)
                rect = QRect(0, 0, clipRect.width(), clipRect.height())
                StyleHelper.verticalGradientHelper(p, spanRect, rect, lightColored)
                p.end()
                QPixmapCache.insert(key, pixmap)
            painter.drawPixmap(clipRect.topLeft(), pixmap)
        else:
            StyleHelper.verticalGradientHelper(painter, spanRect, clipRect, lightColored)

    @staticmethod
    def horizontalGradientHelper(p, spanRect, rect, lightColored):
        if lightColored:
            shadowGradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            shadowGradient.setColorAt(0, 0xf0f0f0)
            shadowGradient.setColorAt(1, 0xcfcfcf)
            p.fillRect(rect, shadowGradient)
            return

        base = StyleHelper.baseColor(lightColored)
        highlight = StyleHelper.highlightColor(lightColored)
        shadow = StyleHelper.shadowColor(lightColored)
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, highlight.lighter(120))
        if rect.height() == StyleHelper.navigationWidgetHeight():
            grad.setColorAt(0.4, highlight)
            grad.setColorAt(0.401, base)

        grad.setColorAt(1, shadow)
        p.fillRect(rect, grad)

        shadowGradient = QLinearGradient(spanRect.topLeft(), spanRect.topRight())
        shadowGradient.setColorAt(0, QColor(0, 0, 0, 30))

        if not lightColored:
            lighterHighlight = highlight.lighter(130)
        else:
            lighterHighlight = highlight.lighter(90)
        lighterHighlight.setAlpha(100)
        shadowGradient.setColorAt(0.7, lighterHighlight)
        shadowGradient.setColorAt(1, QColor(0, 0, 0, 40))
        p.fillRect(rect, shadowGradient)

    @staticmethod
    def horizontalGradient(painter, spanRect, clipRect, lightColored):
        if StyleHelper.usePixmapCache():
            keyColor = StyleHelper.baseColor(lightColored)
            key = "mh_horizontal {0} {1} {2} {3} {4}".format(spanRect.width(),
                                                             spanRect.height(),
                                                             clipRect.width(),
                                                             clipRect.height(),
                                                             keyColor.rgb(),
                                                             spanRect.x())

            pixmap = QPixmap()
            if not QPixmapCache.find(key, pixmap):
                pixmap = QPixmap(clipRect.size())
                p = QPainter(pixmap)
                rect = QRect(0, 0, clipRect.width(), clipRect.height())
                StyleHelper.horizontalGradientHelper(p, spanRect, rect, lightColored)
                p.end()
                QPixmapCache.insert(key, pixmap)

            painter.drawPixmap(clipRect.topLeft(), pixmap)

        else:
            StyleHelper.horizontalGradientHelper(painter, spanRect, clipRect, lightColored)

    @staticmethod
    def menuGradientHelper(p, spanRect, rect):
        grad = QLinearGradient(spanRect.topLeft(), spanRect.bottomLeft())
        menuColor = StyleHelper.mergedColors(StyleHelper.baseColor(), QColor(244, 244, 244), 25)
        grad.setColorAt(0, menuColor.lighter(112))
        grad.setColorAt(1, menuColor)
        p.fillRect(rect, grad)

    @staticmethod
    def drawArrow(element, painter, option):
        # From windows style but modified to enable AA
        if option.rect.width() <= 1 or option.rect.height() <= 1:
            return

        r = option.rect
        size = min(r.height(), r.width())
        pixmap = QPixmap()
        pixmapName = "arrow-{0}-{1}-{2}-{3}-{4}".format("$qt_ia", int(option.state),
                                                        element, size, option.palette.cacheKey())
        if not QPixmapCache.find(pixmapName, pixmap):
            border = size / 5
            sqsize = 2 * (size / 2)
            image = QImage(sqsize, sqsize, QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            imagePainter = QPainter(image)
            imagePainter.setRenderHint(QPainter.Antialiasing, True)
            imagePainter.translate(0.5, 0.5)
            a = QPolygon()
            if element == QStyle.PE_IndicatorArrowUp:
                a.setPoints(3, border, sqsize / 2, sqsize / 2, border, sqsize - border, sqsize / 2)
            elif element == QStyle.PE_IndicatorArrowDown:
                a.setPoints(3, border, sqsize / 2, sqsize / 2, sqsize - border, sqsize - border, sqsize / 2)
            elif element == QStyle.PE_IndicatorArrowRight:
                a.setPoints(3, sqsize - border, sqsize / 2, sqsize / 2, border, sqsize / 2, sqsize - border)
            elif element == QStyle.PE_IndicatorArrowLeft:
                a.setPoints(3, border, sqsize / 2, sqsize / 2, border, sqsize / 2, sqsize - border)
            else:
                pass

        bsx = 0
        bsy = 0

        if option.state & QStyle.State_Sunken:
            bsx = qApp.style().pixelMetric(QStyle.PM_ButtonShiftHorizontal)
            bsy = qApp.style().pixelMetric(QStyle.PM_ButtonShiftVertical)

        bounds = a.boundingRect()
        sx = sqsize / 2 - bounds.center().x() - 1
        sy = sqsize / 2 - bounds.center().y() - 1
        imagePainter.translate(sx + bsx, sy + bsy)

        if not (option.state & QStyle.State_Enabled):
            imagePainter.setBrush(option.palette.mid().color())
            imagePainter.setPen(option.palette.mid().color())
        else:
            shadow = QColor(0, 0, 0, 100)
            imagePainter.translate(0, 1)
            imagePainter.setPen(shadow)
            imagePainter.setBrush(shadow)
            foreGround = QColor(255, 255, 255, 210)
            imagePainter.drawPolygon(a)
            imagePainter.translate(0, -1)
            imagePainter.setPen(foreGround)
            imagePainter.setBrush(foreGround)

        imagePainter.drawPolygon(a)
        imagePainter.end()
        pixmap = QPixmap.fromImage(image)
        QPixmapCache.insert(pixmapName, pixmap)

        xOffset = r.x() + (r.width() - size) / 2
        yOffset = r.y() + (r.height() - size) / 2
        painter.drawPixmap(xOffset, yOffset, pixmap)

    @staticmethod
    def menuGradient(painter, spanRect, clipRect):
        if StyleHelper.usePixmapCache():
            key = "mh_menu {0} {1} {2} {3} {4}".format(spanRect.width(),
                                                       spanRect.height(),
                                                       clipRect.width(),
                                                       clipRect.height(),
                                                       StyleHelper.baseColor().rgb())
            pixmap = QPixmap()
            if not QPixmapCache.find(key, pixmap):
                pixmap = QPixmap(clipRect.size())
                p = QPainter(pixmap)
                rect = QRect(0, 0, clipRect.width(), clipRect.height())
                StyleHelper.menuGradientHelper(p, spanRect, rect)

            painter.drawPixmap(clipRect.topLeft(), pixmap)
        else:
            StyleHelper.menuGradientHelper(painter, spanRect, clipRect)

    @staticmethod
    def usePixmapCache():
        return True

    @staticmethod
    def drawIconWithShadow(icon, rect, p, iconMode, radius, color, offset):
        cache = QPixmap()
        pixmapName = "icon {0} {1} {2}".format(icon.cacheKey(), iconMode, rect.height())

        if not QPixmapCache.find(pixmapName, cache):
            px = icon.pixmap(rect.size())
            cache = QPixmap(px.size() + QSize(radius * 2, radius * 2))
            cache.fill(Qt.transparent)

            cachePainter = QPainter(cache)
            if iconMode == QIcon.Disabled:
                im = px.toImage().convertToFormat(QImage.Format_ARGB32)
                for y in range(im.height()):
                    scanLine = im.scanLine(y)
                    for x in range(im.width()):
                        pixel = scanLine
                        intensity = qGray(pixel)
                        scanLine = qRgba(intensity, intensity, intensity, qAlpha(pixel))
                        scanLine += 1
                px = QPixmap.fromImage(im)

            # Draw shadow
            tmp = QImage(px.size() + QSize(radius * 2, radius * 2 + 1),
                         QImage.Format_ARGB32_Premultiplied)
            tmp.fill(Qt.transparent)

            tmpPainter = QPainter(tmp)
            tmpPainter.setCompositionMode(QPainter.CompositionMode_Source)
            tmpPainter.drawPixmap(QPoint(radius, radius), px)
            tmpPainter.end()

            # blur the alpha channel
            blurred = QImage(tmp.size(), QImage.Format_ARGB32_Premultiplied)
            blurred.fill(Qt.transparent)
            blurPainter = QPainter(blurred)
            # todo : blur image
            blurPainter.end()

            tmp = blurred

            # blacken the image
            tmpPainter.begin(tmp)
            tmpPainter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            tmpPainter.fillRect(tmp.rect(), color)
            tmpPainter.end()

            tmpPainter.begin(tmp)
            tmpPainter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            tmpPainter.fillRect(tmp.rect(), color)
            tmpPainter.end()

            # draw the blurred drop shadow...
            cachePainter.drawImage(QRect(0, 0, cache.rect().width(), cache.rect().height()), tmp)

            # Draw the actual pixmap...
            cachePainter.drawPixmap(QPoint(radius, radius) + offset, px)
            QPixmapCache.insert(pixmapName, cache)

        targetRect = cache.rect()
        targetRect.moveCenter(rect.center())
        p.drawPixmap(targetRect.topLeft() - offset, cache)

    @staticmethod
    def drawCornerImage(img, painter, rect, left, top, right, bottom):
        size = img.size()
        if top:
            painter.drawImage(QRect(rect.left() + left, rect.top(), rect.width() - right - left, top), img,
                              QRect(left, 0, size.width() - right - left, top))
            if left > 0:
                painter.drawImage(QRect(rect.left(), rect.top(), left, top), img,
                                  QRect(0, 0, left, top))
            if right > 0:
                painter.drawImage(QRect(rect.left() + rect.width() - right, rect.top(), right, top), img,
                                  QRect(size.width() - right, 0, right, top))
        if left > 0:
            painter.drawImage(QRect(rect.left(), rect.top() + top, left, rect.height() - top - bottom), img,
                              QRect(0, top, left, size.height() - bottom - top))
        painter.drawImage(QRect(rect.left() + left, rect.top() + top, rect.width() - right - left,
                          rect.height() - bottom - top), img, QRect(left, top, size.width() - right - left,
                                                                    size.height() - bottom - top))
        if right > 0:
            painter.drawImage(QRect(rect.left() + left, rect.top() + rect.height() - bottom,
                                    rect.width() - right - left, bottom), img,
                              QRect(left, size.height() - bottom, size.width() - right - left, bottom))
        if bottom > 0:
            painter.drawImage(QRect(rect.left() + left, rect.top() + rect.height() - bottom,
                                    rect.width() - right - left, bottom), img,
                              QRect(left, size.height() - bottom, size.width() - right - left, bottom))
        if left > 0:
            painter.drawImage(QRect(rect.left(), rect.top() + rect.height() - bottom, left, bottom), img,
                              QRect(0, size.height() - bottom, left, bottom))
        if right > 0:
            painter.drawImage(QRect(rect.left() + rect.width() - right, rect.top() + rect.height() - bottom,
                                    right, bottom), img,
                              QRect(size.width() - right, size.height() - bottom, right, bottom))
