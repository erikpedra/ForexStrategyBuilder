# Williams' Percent Range Indicator
# Last changed on 2009-05-05
# Part of Forex Strategy Builder & Forex Strategy Trader
# Website http://forexsb.com/
# Copyright (c) 2006 - 2011 Miroslav Popov - All rights reserved.
# This code or any part of it cannot be used in other applications without a permission.


class Forex_Strategy_Builder: #this class replaces the original namespace 'Forex_Strategy_Builder'
    #/ <summary>
    #/ Indicator Williams' Percent Range
    #/ </summary>
    class Williams_Percent_Range(Indicator):
        #/ <summary>
        #/ Sets the default indicator parameters for the designated slot type
        #/ </summary>
        def __init__(self, slotType):
            # General properties
            IndicatorName = "Williams' Percent Range"
            PossibleSlots = SlotTypes.OpenFilter | SlotTypes.CloseFilter
            SeparatedChart = True
            SeparatedChartMinValue = -100
            SeparatedChartMaxValue = 0

            # Setting up the indicator parameters
            IndParam = IndicatorParam()
            IndParam.IndicatorName = IndicatorName
            IndParam.SlotType = slotType

            # The ComboBox parameters
            IndParam.ListParam[0].Caption = "Logic"
            IndParam.ListParam[0].ItemList = ["The %R rises", "The %R falls", "The %R is higher than the Level line", "The %R is lower than the Level line", "The %R crosses the Level line upward", "The %R crosses the Level line downward", "The %R changes its direction upward", "The %R changes its direction downward"]
            IndParam.ListParam[0].Index = 0
            IndParam.ListParam[0].Text = IndParam.ListParam[0].ItemList[IndParam.ListParam[0].Index]
            IndParam.ListParam[0].Enabled = True
            IndParam.ListParam[0].ToolTip = "Logic of application of the indicator."

            IndParam.ListParam[1].Caption = "Smoothing method"
            IndParam.ListParam[1].ItemList = Enum.GetNames(typeof(MAMethod))
            IndParam.ListParam[1].Index = int(MAMethod.Simple)
            IndParam.ListParam[1].Text = IndParam.ListParam[1].ItemList[IndParam.ListParam[1].Index]
            IndParam.ListParam[1].Enabled = True
            IndParam.ListParam[1].ToolTip = "The Moving Average method used for smoothing."

            IndParam.NumParam[0].Caption = "Period of %R"
            IndParam.NumParam[0].Value = 14
            IndParam.NumParam[0].Min = 1
            IndParam.NumParam[0].Max = 200
            IndParam.NumParam[0].Enabled = True
            IndParam.NumParam[0].ToolTip = "The period of calculation."

            IndParam.NumParam[1].Caption = "Smoothing period"
            IndParam.NumParam[1].Value = 0
            IndParam.NumParam[1].Min = 0
            IndParam.NumParam[1].Max = 200
            IndParam.NumParam[1].Enabled = True
            IndParam.NumParam[1].ToolTip = "The period of an additional smoothing."

            IndParam.NumParam[2].Caption = "Level"
            IndParam.NumParam[2].Value = -20
            IndParam.NumParam[2].Min = -100
            IndParam.NumParam[2].Max = 0
            IndParam.NumParam[2].Enabled = True
            IndParam.NumParam[2].ToolTip = "A critical level (for the appropriate logic)."

            # The CheckBox parameters.
            IndParam.CheckParam[0].Caption = "Use previous bar value"
            IndParam.CheckParam[0].Checked = PrepareUsePrevBarValueCheckBox(slotType)
            IndParam.CheckParam[0].Enabled = True
            IndParam.CheckParam[0].ToolTip = "Use the indicator value from the previous bar."

            return

        #/ <summary>
        #/ Calculates the indicator's components
        #/ </summary>
        def Calculate(self, slotType):
            # Reading the parameters
            maMethod = IndParam.ListParam[1].Index
            iPeriod = int(IndParam.NumParam[0].Value)
            iSmoothing = int(IndParam.NumParam[1].Value)
            dLevel = int(IndParam.NumParam[2].Value)
            iPrvs = 1 if IndParam.CheckParam[0].Checked else 0

            # Calculation
            iFirstBar = iPeriod + iSmoothing + iPrvs + 2

            adR = [0 for _ in range(Bars)]
            dMin = double.MaxValue
            dMax = double.MinValue
            iBar = iPeriod
            while iBar < Bars:
                dMin = double.MaxValue
                dMax = double.MinValue
                for index in range(0, iPeriod):
                    if High[iBar - index] > dMax:
                        dMax = High[iBar - index]
                    if Low [iBar - index] < dMin:
                        dMin = Low [iBar - index]
                adR[iBar] = -100 * (dMax - Close[iBar]) / (dMax - dMin)
                iBar += 1

            adRSmoothed = MovingAverage(iSmoothing, 0, maMethod, adR)

            # Saving the components
            Component = [None for _ in range(3)]

            Component[0] = IndicatorComp()
            Component[0].CompName = "%R"
            Component[0].DataType = IndComponentType.IndicatorValue
            Component[0].ChartType = IndChartType.Line
            Component[0].ChartColor = Color.Teal
            Component[0].FirstBar = iFirstBar
            Component[0].Value = adRSmoothed

            Component[1] = IndicatorComp()
            Component[1].ChartType = IndChartType.NoChart
            Component[1].FirstBar = iFirstBar
            Component[1].Value = [0 for _ in range(Bars)]

            Component[2] = IndicatorComp()
            Component[2].ChartType = IndChartType.NoChart
            Component[2].FirstBar = iFirstBar
            Component[2].Value = [0 for _ in range(Bars)]

            # Sets the Component's type
            if slotType is SlotTypes.OpenFilter:
                Component[1].DataType = IndComponentType.AllowOpenLong
                Component[1].CompName = "Is long entry allowed"
                Component[2].DataType = IndComponentType.AllowOpenShort
                Component[2].CompName = "Is short entry allowed"
            elif slotType is SlotTypes.CloseFilter:
                Component[1].DataType = IndComponentType.ForceCloseLong
                Component[1].CompName = "Close out long position"
                Component[2].DataType = IndComponentType.ForceCloseShort
                Component[2].CompName = "Close out short position"

            # Calculation of the logic
            indLogic = IndicatorLogic.It_does_not_act_as_a_filter

            if IndParam.ListParam[0].Text == "The %R rises":
                indLogic = IndicatorLogic.The_indicator_rises
                SpecialValues = [-50]

            elif IndParam.ListParam[0].Text == "The %R falls":
                indLogic = IndicatorLogic.The_indicator_falls
                SpecialValues = [-50]

            elif IndParam.ListParam[0].Text == "The %R is higher than the Level line":
                indLogic = IndicatorLogic.The_indicator_is_higher_than_the_level_line
                SpecialValues = [dLevel, -100 - dLevel]

            elif IndParam.ListParam[0].Text == "The %R is lower than the Level line":
                indLogic = IndicatorLogic.The_indicator_is_lower_than_the_level_line
                SpecialValues = [dLevel, -100 - dLevel]

            elif IndParam.ListParam[0].Text == "The %R crosses the Level line upward":
                indLogic = IndicatorLogic.The_indicator_crosses_the_level_line_upward
                SpecialValues = [dLevel, -100 - dLevel]

            elif IndParam.ListParam[0].Text == "The %R crosses the Level line downward":
                indLogic = IndicatorLogic.The_indicator_crosses_the_level_line_downward
                SpecialValues = [dLevel, -100 - dLevel]

            elif IndParam.ListParam[0].Text == "The %R changes its direction upward":
                indLogic = IndicatorLogic.The_indicator_changes_its_direction_upward
                SpecialValues = [-50]

            elif IndParam.ListParam[0].Text == "The %R changes its direction downward":
                indLogic = IndicatorLogic.The_indicator_changes_its_direction_downward
                SpecialValues = [-50]


# C# TO PYTHON CONVERTER TASK: The following method call contained an unresolved 'ref' keyword - these cannot be converted using the 'RefObject' helper class unless the method is within the code being modified:
            OscillatorLogic(iFirstBar, iPrvs, adRSmoothed, dLevel, -100 - dLevel, ref Component[1], ref Component[2], indLogic)

            return

        #/ <summary>
        #/ Sets the indicator logic description
        #/ </summary>
        def SetDescription(self, slotType):
            sLevelLong = IndParam.NumParam[2].ValueToString
            sLevelShort = IndParam.NumParam[2].AnotherValueToString(-100 - IndParam.NumParam[2].Value)

            EntryFilterLongDescription = "the " + self.ToString() + " "
            EntryFilterShortDescription = "the " + self.ToString() + " "
            ExitFilterLongDescription = "the " + self.ToString() + " "
            ExitFilterShortDescription = "the " + self.ToString() + " "

            if IndParam.ListParam[0].Text == "The %R rises":
                EntryFilterLongDescription += "rises"
                EntryFilterShortDescription += "falls"
                ExitFilterLongDescription += "rises"
                ExitFilterShortDescription += "falls"

            elif IndParam.ListParam[0].Text == "The %R falls":
                EntryFilterLongDescription += "falls"
                EntryFilterShortDescription += "rises"
                ExitFilterLongDescription += "falls"
                ExitFilterShortDescription += "rises"

            elif IndParam.ListParam[0].Text == "The %R is higher than the Level line":
                EntryFilterLongDescription += "is higher than the Level " + sLevelLong
                EntryFilterShortDescription += "is lower than the Level " + sLevelShort
                ExitFilterLongDescription += "is higher than the Level " + sLevelLong
                ExitFilterShortDescription += "is lower than the Level " + sLevelShort

            elif IndParam.ListParam[0].Text == "The %R is lower than the Level line":
                EntryFilterLongDescription += "is lower than the Level " + sLevelLong
                EntryFilterShortDescription += "is higher than the Level " + sLevelShort
                ExitFilterLongDescription += "is lower than the Level " + sLevelLong
                ExitFilterShortDescription += "is higher than the Level " + sLevelShort

            elif IndParam.ListParam[0].Text == "The %R crosses the Level line upward":
                EntryFilterLongDescription += "crosses the Level " + sLevelLong + " upward"
                EntryFilterShortDescription += "crosses the Level " + sLevelShort + " downward"
                ExitFilterLongDescription += "crosses the Level " + sLevelLong + " upward"
                ExitFilterShortDescription += "crosses the Level " + sLevelShort + " downward"

            elif IndParam.ListParam[0].Text == "The %R crosses the Level line downward":
                EntryFilterLongDescription += "crosses the Level " + sLevelLong + " downward"
                EntryFilterShortDescription += "crosses the Level " + sLevelShort + " upward"
                ExitFilterLongDescription += "crosses the Level " + sLevelLong + " downward"
                ExitFilterShortDescription += "crosses the Level " + sLevelShort + " upward"

            elif IndParam.ListParam[0].Text == "The %R changes its direction upward":
                EntryFilterLongDescription += "changes its direction upward"
                EntryFilterShortDescription += "changes its direction downward"
                ExitFilterLongDescription += "changes its direction upward"
                ExitFilterShortDescription += "changes its direction downward"

            elif IndParam.ListParam[0].Text == "The %R changes its direction downward":
                EntryFilterLongDescription += "changes its direction downward"
                EntryFilterShortDescription += "changes its direction upward"
                ExitFilterLongDescription += "changes its direction downward"
                ExitFilterShortDescription += "changes its direction upward"


            return

        #/ <summary>
        #/ Indicator to string
        #/ </summary>
        def ToString(self):
            sString = IndicatorName + ("* (" if IndParam.CheckParam[0].Checked else " (") + IndParam.ListParam[1].Text + ", " + IndParam.NumParam[0].ValueToString + ", " + IndParam.NumParam[1].ValueToString + ")" # Smoothing period

            return sString
