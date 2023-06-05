(ns quo2.components.wallet.account-card.style
  (:require
    [quo2.foundations.colors :as colors]))

(defn card
  [customization-color]
  {:width              180
   :background-color   (colors/custom-color customization-color 50)
   :border-radius      16
   :padding-horizontal 12
   :padding-top        8
   :padding-bottom     10})


(def profile-container
  {:margin-bottom  8
   :flex-direction "row"})

(def metrics-container
  {:flex-direction "row"
   :align-items    "center"})

(def title
  {:margin-bottom 9})

(def account-name
  {:number-of-lines 1
   :weight          :semi-bold
   :size            :paragraph-1
   :style           {:color       colors/white
                     :margin-left 5}})

(def account-value
  {:size   :heading-2
   :weight :semi-bold
   :style  {:color colors/white}})

(def percentage-circle
  {:width           20
   :height          20
   :margin-right    5.5
   :align-items     "center"
   :justify-content "center"})

(def value
  {:weight :semi-bold
   :style  {:color colors/white-opa-70}})

(def separator
  {:width             1
   :height            10
   :border-width      1
   :borderColor       colors/white-opa-40
   :margin-horizontal 4})
