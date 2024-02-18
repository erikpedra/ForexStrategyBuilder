# ADX Indicator
# Last changed on 2010-07-15
# Copyright (c) 2006 - 2011 Miroslav Popov - All rights reserved.
# Part of Forex Strategy Builder & Forex Strategy Trader
# Website http://forexsb.com
# This code or any part of it cannot be used in other applications without a permission.


class Forex_Strategy_Builder: #this class replaces the original namespace 'Forex_Strategy_Builder'
    #/ <summary>
    #/ ADX Indicator
    #/ </summary>
    class ADX(Indicator):
        #/ <summary>
        #/ Sets the default indicator parameters for the designated slot type
        #/ </summary>
        def __init__(self, slotType):
            # General properties
            IndicatorName = "ADX"
            PossibleSlots = SlotTypes.OpenFilter | SlotTypes.CloseFilter
            SeparatedChart = True
            SeparatedChartMinValue = 0

            # Setting up the indicator parameters
            IndParam = IndicatorParam()
            IndParam.IndicatorName = IndicatorName
            IndParam.SlotType = slotType

            # The ComboBox parameters
            IndParam.ListParam[0].Caption = "Logic"
            IndParam.ListParam[0].ItemList = ["The ADX rises", "The ADX falls", "The ADX is higher than the Level line", "The ADX is lower than the Level line", "The ADX crosses the Level line upward", "The ADX crosses the Level line downward", "The ADX changes its direction upward", "The ADX changes its direction downward"]
            IndParam.ListParam[0].Index = 0
            IndParam.ListParam[0].Text = IndParam.ListParam[0].ItemList[IndParam.ListParam[0].Index]
            IndParam.ListParam[0].Enabled = True
            IndParam.ListParam[0].ToolTip = "Logic of application of the indicator."

            IndParam.ListParam[1].Caption = "Smoothing method"
            IndParam.ListParam[1].ItemList = Enum.GetNames(typeof(MAMethod))
            IndParam.ListParam[1].Index = int(MAMethod.Exponential)
            IndParam.ListParam[1].Text = IndParam.ListParam[1].ItemList[IndParam.ListParam[1].Index]
            IndParam.ListParam[1].Enabled = True
            IndParam.ListParam[1].ToolTip = "The Moving Average method used for smoothing the ADX value."

            IndParam.ListParam[2].Caption = "Base price"
            IndParam.ListParam[2].ItemList = ["Bar range"]
            IndParam.ListParam[2].Index = 0
            IndParam.ListParam[2].Text = IndParam.ListParam[2].ItemList[IndParam.ListParam[2].Index]
            IndParam.ListParam[2].Enabled = True
            IndParam.ListParam[2].ToolTip = "ADX uses current and previous bar ranges."

            # The NumericUpDown parameters
            IndParam.NumParam[0].Caption = "Period"
            IndParam.NumParam[0].Value = 14
            IndParam.NumParam[0].Min = 1
            IndParam.NumParam[0].Max = 200
            IndParam.NumParam[0].Enabled = True
            IndParam.NumParam[0].ToolTip = "The period of ADX."

            IndParam.NumParam[1].Caption = "Level"
            IndParam.NumParam[1].Value = 0
            IndParam.NumParam[1].Min = 0
            IndParam.NumParam[1].Max = 100
            IndParam.NumParam[1].Point = 0
            IndParam.NumParam[1].Enabled = True
            IndParam.NumParam[1].ToolTip = "A critical level (for the appropriate logic)."

            # The CheckBox parameters
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
            period = int(IndParam.NumParam[0].Value)
            level = IndParam.NumParam[1].Value
            prev = 1 if IndParam.CheckParam[0].Checked else 0

            # Calculation
            firstBar = 2 * period + 2

            DIPos = [0 for _ in range(Bars)]
            DINeg = [0 for _ in range(Bars)]

            bar = 1
            while bar < Bars:
                trueRange = max(High[bar], Close[bar - 1]) - min(Low[bar], Close[bar - 1])

                if trueRange < Point:
                    trueRange = Point

                deltaHigh = High[bar] - High[bar - 1]
                deltaLow = Low[bar - 1] - Low[bar]

                if deltaHigh > 0 and deltaHigh > deltaLow:
                    DIPos[bar] = 100 * deltaHigh / trueRange
                else:
                    DIPos[bar] = 0

                if deltaLow > 0 and deltaLow > deltaHigh:
                    DINeg[bar] = 100 * deltaLow / trueRange
                else:
                    DINeg[bar] = 0
                bar += 1

            ADIPos = MovingAverage(period, 0, maMethod, DIPos)
            ADINeg = MovingAverage(period, 0, maMethod, DINeg)

            DX = [0 for _ in range(Bars)]

            bar = 0
            while bar < Bars:
                if ADIPos[bar] + ADINeg[bar] == 0:
                    DX[bar] = 0
                else:
                    DX[bar] = 100 * abs((ADIPos[bar] - ADINeg[bar]) / (ADIPos[bar] + ADINeg[bar]))
                bar += 1

            ADX = MovingAverage(period, 0, maMethod, DX)

            # Saving the components
            Component = [None for _ in range(5)]

            Component[0] = IndicatorComp()
            Component[0].CompName = "ADX"
            Component[0].DataType = IndComponentType.IndicatorValue
            Component[0].ChartType = IndChartType.Line
            Component[0].ChartColor = Color.Blue
            Component[0].FirstBar = firstBar
            Component[0].Value = ADX

            Component[1] = IndicatorComp()
            Component[1].CompName = "ADI+"
            Component[1].DataType = IndComponentType.IndicatorValue
            Component[1].ChartType = IndChartType.Line
            Component[1].ChartColor = Color.Green
            Component[1].FirstBar = firstBar
            Component[1].Value = ADIPos

            Component[2] = IndicatorComp()
            Component[2].CompName = "ADI-"
            Component[2].DataType = IndComponentType.IndicatorValue
            Component[2].ChartType = IndChartType.Line
            Component[2].ChartColor = Color.Red
            Component[2].FirstBar = firstBar
            Component[2].Value = ADINeg

            Component[3] = IndicatorComp()
            Component[3].ChartType = IndChartType.NoChart
            Component[3].FirstBar = firstBar
            Component[3].Value = [0 for _ in range(Bars)]

            Component[4] = IndicatorComp()
            Component[4].ChartType = IndChartType.NoChart
            Component[4].FirstBar = firstBar
            Component[4].Value = [0 for _ in range(Bars)]

            # Sets the Component's type
            if slotType is SlotTypes.OpenFilter:
                Component[3].DataType = IndComponentType.AllowOpenLong
                Component[3].CompName = "Is long entry allowed"
                Component[4].DataType = IndComponentType.AllowOpenShort
                Component[4].CompName = "Is short entry allowed"
            elif slotType is SlotTypes.CloseFilter:
                Component[3].DataType = IndComponentType.ForceCloseLong
                Component[3].CompName = "Close out long position"
                Component[4].DataType = IndComponentType.ForceCloseShort
                Component[4].CompName = "Close out short position"

            # Calculation of the logic
            logicRule = None

            if IndParam.ListParam[0].Text == "The ADX rises":
                logicRule = IndicatorLogic.The_indicator_rises

            elif IndParam.ListParam[0].Text == "The ADX falls":
                logicRule = IndicatorLogic.The_indicator_falls

            elif IndParam.ListParam[0].Text == "The ADX is higher than the Level line":
                logicRule = IndicatorLogic.The_indicator_is_higher_than_the_level_line
                SpecialValues = [level]

            elif IndParam.ListParam[0].Text == "The ADX is lower than the Level line":
                logicRule = IndicatorLogic.The_indicator_is_lower_than_the_level_line
                SpecialValues = [level]

            elif IndParam.ListParam[0].Text == "The ADX crosses the Level line upward":
                logicRule = IndicatorLogic.The_indicator_crosses_the_level_line_upward
                SpecialValues = [level]

            elif IndParam.ListParam[0].Text == "The ADX crosses the Level line downward":
                logicRule = IndicatorLogic.The_indicator_crosses_the_level_line_downward
                SpecialValues = [level]

            elif IndParam.ListParam[0].Text == "The ADX changes its direction upward":
                logicRule = IndicatorLogic.The_indicator_changes_its_direction_upward

            elif IndParam.ListParam[0].Text == "The ADX changes its direction downward":
                logicRule = IndicatorLogic.The_indicator_changes_its_direction_downward

            else:
                logicRule = IndicatorLogic.It_does_not_act_as_a_filter

            # ADX rises equal signals in both directions!
# C# TO PYTHON CONVERTER TASK: The following method call contained an unresolved 'ref' keyword - these cannot be converted using the 'RefObject' helper class unless the method is within the code being modified:
            NoDirectionOscillatorLogic(firstBar, prev, ADX, level, ref Component[3], logicRule)
            Component[4].Value = Component[3].Value

            return

        #/ <summary>
        #/ Sets the indicator logic description
        #/ </summary>
        def SetDescription(self, slotType):
            sLevelLong = IndParam.NumParam[1].ValueToString
            sLevelShort = sLevelLong

            EntryFilterLongDescription = "the " + self.ToString() + " "
            EntryFilterShortDescription = "the " + self.ToString() + " "
            ExitFilterLongDescription = "the " + self.ToString() + " "
            ExitFilterShortDescription = "the " + self.ToString() + " "

            if IndParam.ListParam[0].Text == "The ADX rises":
                EntryFilterLongDescription += "rises"
                EntryFilterShortDescription += "rises"
                ExitFilterLongDescription += "rises"
                ExitFilterShortDescription += "rises"

            elif IndParam.ListParam[0].Text == "The ADX falls":
                EntryFilterLongDescription += "falls"
                EntryFilterShortDescription += "falls"
                ExitFilterLongDescription += "falls"
                ExitFilterShortDescription += "falls"

            elif IndParam.ListParam[0].Text == "The ADX is higher than the Level line":
                EntryFilterLongDescription += "is higher than the Level " + sLevelLong
                EntryFilterShortDescription += "is higher than the Level " + sLevelShort
                ExitFilterLongDescription += "is higher than the Level " + sLevelLong
                ExitFilterShortDescription += "is higher than the Level " + sLevelShort

            elif IndParam.ListParam[0].Text == "The ADX is lower than the Level line":
                EntryFilterLongDescription += "is lower than the Level " + sLevelLong
                EntryFilterShortDescription += "is lower than the Level " + sLevelShort
                ExitFilterLongDescription += "is lower than the Level " + sLevelLong
                ExitFilterShortDescription += "is lower than the Level " + sLevelShort

            elif IndParam.ListParam[0].Text == "The ADX crosses the Level line upward":
                EntryFilterLongDescription += "crosses the Level " + sLevelLong + " upward"
                EntryFilterShortDescription += "crosses the Level " + sLevelShort + " upward"
                ExitFilterLongDescription += "crosses the Level " + sLevelLong + " upward"
                ExitFilterShortDescription += "crosses the Level " + sLevelShort + " upward"

            elif IndParam.ListParam[0].Text == "The ADX crosses the Level line downward":
                EntryFilterLongDescription += "crosses the Level " + sLevelLong + " downward"
                EntryFilterShortDescription += "crosses the Level " + sLevelShort + " downward"
                ExitFilterLongDescription += "crosses the Level " + sLevelLong + " downward"
                ExitFilterShortDescription += "crosses the Level " + sLevelShort + " downward"

            elif IndParam.ListParam[0].Text == "The ADX changes its direction upward":
                EntryFilterLongDescription += "changes its direction upward"
                EntryFilterShortDescription += "changes its direction upward"
                ExitFilterLongDescription += "changes its direction upward"
                ExitFilterShortDescription += "changes its direction upward"

            elif IndParam.ListParam[0].Text == "The ADX changes its direction downward":
                EntryFilterLongDescription += "changes its direction downward"
                EntryFilterShortDescription += "changes its direction downward"
                ExitFilterLongDescription += "changes its direction downward"
                ExitFilterShortDescription += "changes its direction downward"


            return

        #/ <summary>
        #/ Indicator to string
        #/ </summary>
        def ToString(self):
            indicator = IndicatorName + ("* (" if IndParam.CheckParam[0].Checked else " (") + IndParam.ListParam[1].Text + ", " + IndParam.ListParam[2].Text + ", " + IndParam.NumParam[0].ValueToString + ")" # ADX Period

            return indicator
