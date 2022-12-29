"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProject,
                       QgsProcessingParameterFeatureSink)
from qgis import processing


class anint(QgsProcessingAlgorithm):

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_BATHY = 'INPUT_BATHY'
    INPUT_CL = 'INPUT_CL'
    INPUT_MASK = 'INPUT_MASK'
    INPUT_P = 'INPUT_P'
    INPUT_GRID_SPACE = 'INPUT_GRID_SPACE'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        # returns a translatable string for use in languages other than English
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return anint()

    def name(self):
        # returns algorithm name for internal tracking
        return 'anint'

    def displayName(self):
        # returns algorithm name for display
        return self.tr('Anisotropic IDW Interpolation')

    def group(self):
        # returns name of group algorithm belongs to for display
        return self.tr('Millsap Scripts')

    def groupId(self):
        # returns name of group algorithm belongs to for internal tracking
        return 'millsapscripts'

    def shortHelpString(self):
        # returns short string describing algorithm
        return self.tr("Anisotropic IDW Interpolation for Bathymetric Data")

    def initAlgorithm(self, config=None):
        self.GridOpts = [self.tr('To Coordinate System'), self.tr('Orthogonal to Centerline')]
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_BATHY,
                self.tr('Bathymetry layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_CL,
                self.tr('Centerline layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_MASK,
                self.tr('Boundary Polygon'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_GRID_SPACE,
                self.tr('Output Grid Spacing'),
                minValue = 1.00,
                maxValue = 1000000.00,
                defaultValue = 3.00,
                type=QgsProcessingParameterNumber.Double
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_P,
                self.tr('Distance Parameter P'),
                minValue=0.00,
                maxValue=100.00,
                defaultValue=2.00,
                type=QgsProcessingParameterNumber.Double
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # create temp layers of bathymetry, centerline, and mask
        bathy_lyr = self.parameterAsVectorLayer(parameters, self.INPUT_BATHY, context)
        cl_lyr = self.parameterAsVectorLayer(parameters, self.INPUT_CL, context)
        mask_lyr = self.parameterAsVectorLayer(parameters, self.INPUT_MASK, context)

        # calculate extents of bathymetry
        bathy_extent = bathy_lyr.extent()
        
        # get CRS from the three layers
        bathy_crs = bathy_lyr.crs()
        cl_crs = cl_lyr.crs()
        mask_crs = mask_lyr.crs()

        # if CRS's don't match, end process
        if bathy_crs != cl_crs:
            raise QgsProcessingException('mismatched CRS in input layers')
        elif bathy_crs != mask_crs:
            raise QgsProcessingException('mismatched CRS in input layers')

        # check CL layer only has one geometry
        cl_feature_count = cl_lyr.featureCount()
        if cl_feature_count > 1:
            raise QgsProcessingException('multiple geometries in centerline layer')

        # create grid layer based on parameters
        grid_layer = processing.run("qgis:regularpoints", {
            'EXTENT':bathy_extent,
            'SPACING':parameters['INPUT_GRID_SPACE'],
            'INSET':0,
            'RANDOMIZE':False,
            'IS_SPACING':True,
            'CRS':bathy_crs,
            'OUTPUT':'memory:'
            }
            ) 

        # clip grid layer
        clipped_layer = processing.run("native:clip", {
            'INPUT':grid_layer,
            'OVERLAY':mask_lyr,
            'OUTPUT':'memory:'
            })

        # create list of segments in centerline
        cl_feature = cl_lyr.getFeatures()
        cl_geom = cl_feature.geometry()
        segments = cl_geom.parts()
        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT_BATHY,
            context
        )

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_BATHY))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # return results
        return {self.OUTPUT: dest_id}
