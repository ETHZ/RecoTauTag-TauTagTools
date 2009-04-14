#!/bin/bash

cmscond_export_iov \
        -s sqlite_file:TancLocal.db                    \
        -i TauNeuralClassifier                         \
        -D CondFormatsPhysicsToolsObjects              \
        -P /afs/cern.ch/cms/DB/conddb                  \
        -t TauNeuralClassifier22X                      \
        -d oracle://cms_orcoff_prep/CMS_COND_BTAU      
