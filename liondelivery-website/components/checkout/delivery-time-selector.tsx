"use client";

import { useState, useEffect } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Clock, Calendar, Loader2, Zap, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { schedulingApi, type DateSlots, type TimeSlot } from "@/lib/api/scheduling";
import { cn } from "@/lib/utils/cn";

interface DeliveryTimeSelectorProps {
  restaurantId: number;
  onSelect: (scheduledTime: string | null) => void;
  selectedTime: string | null;
}

export function DeliveryTimeSelector({
  restaurantId,
  onSelect,
  selectedTime,
}: DeliveryTimeSelectorProps) {
  const locale = useLocale();
  const t = useTranslations("checkout.scheduling");
  const isRTL = locale === "ar";
  const [isScheduled, setIsScheduled] = useState(false);
  const [dates, setDates] = useState<DateSlots[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch delivery slots when scheduling is enabled
  useEffect(() => {
    if (isScheduled && restaurantId) {
      setIsLoading(true);
      setError(null);

      schedulingApi
        .getSlots(restaurantId)
        .then((response) => {
          setDates(response.dates);
          // Select the first date by default
          if (response.dates.length > 0 && !selectedDate) {
            setSelectedDate(response.dates[0].date);
          }
        })
        .catch((err) => {
          console.error("Failed to fetch delivery slots:", err);
          setError(isRTL ? "فشل في تحميل الاوقات" : "Failed to load time slots");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [isScheduled, restaurantId, isRTL]);

  const handleAsapClick = () => {
    setIsScheduled(false);
    onSelect(null);
    setSelectedDate(null);
  };

  const handleScheduleClick = () => {
    setIsScheduled(true);
  };

  const handleDateSelect = (date: string) => {
    setSelectedDate(date);
    // Clear time selection when date changes
    onSelect(null);
  };

  const handleTimeSelect = (slot: TimeSlot) => {
    onSelect(slot.datetime);
  };

  const selectedDateData = dates.find((d) => d.date === selectedDate);

  // Format date for display
  const formatDateDisplay = (dateStr: string, displayStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return isRTL ? "اليوم" : "Today";
    }
    if (date.toDateString() === tomorrow.toDateString()) {
      return isRTL ? "غدا" : "Tomorrow";
    }

    // Format as day name in Arabic
    if (isRTL) {
      const days = ["الاحد", "الاثنين", "الثلاثاء", "الاربعاء", "الخميس", "الجمعة", "السبت"];
      return days[date.getDay()];
    }

    return displayStr;
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100">
          <Clock className="h-5 w-5 text-emerald-600" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{t("title")}</h3>
          <p className="text-sm text-gray-500">
            {isRTL ? "متى تريد استلام طلبك؟" : "When would you like your order?"}
          </p>
        </div>
      </div>

      {/* ASAP vs Schedule Toggle */}
      <div className="flex gap-3">
        <button
          type="button"
          onClick={handleAsapClick}
          className={cn(
            "flex flex-1 items-center justify-center gap-2 rounded-xl border-2 px-4 py-3 font-medium transition-all",
            !isScheduled
              ? "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm"
              : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
          )}
        >
          <Zap className={cn("h-5 w-5", !isScheduled ? "text-emerald-500" : "text-gray-400")} />
          {t("asap")}
          {!isScheduled && (
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500">
              <Check className="h-3 w-3 text-white" />
            </div>
          )}
        </button>
        <button
          type="button"
          onClick={handleScheduleClick}
          className={cn(
            "flex flex-1 items-center justify-center gap-2 rounded-xl border-2 px-4 py-3 font-medium transition-all",
            isScheduled
              ? "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm"
              : "border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50"
          )}
        >
          <Calendar className={cn("h-5 w-5", isScheduled ? "text-emerald-500" : "text-gray-400")} />
          {t("schedule")}
          {isScheduled && (
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500">
              <Check className="h-3 w-3 text-white" />
            </div>
          )}
        </button>
      </div>

      {/* Scheduling Options */}
      <AnimatePresence>
        {isScheduled && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="space-y-4 overflow-hidden"
          >
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex flex-col items-center gap-2">
                  <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
                  <p className="text-sm text-gray-500">
                    {isRTL ? "جاري التحميل..." : "Loading..."}
                  </p>
                </div>
              </div>
            ) : error ? (
              <div className="rounded-xl bg-red-50 p-4 text-center text-sm text-red-600">
                {error}
              </div>
            ) : (
              <>
                {/* Date Selection */}
                <div>
                  <label className="mb-3 block text-sm font-medium text-gray-700">
                    {t("selectDate")}
                  </label>
                  <div className="scrollbar-hide flex gap-2 overflow-x-auto pb-2">
                    {dates.slice(0, 7).map((dateData) => {
                      const isSelected = selectedDate === dateData.date;
                      return (
                        <button
                          key={dateData.date}
                          type="button"
                          onClick={() => handleDateSelect(dateData.date)}
                          className={cn(
                            "flex min-w-[85px] flex-col items-center rounded-xl border-2 px-4 py-3 transition-all",
                            isSelected
                              ? "border-emerald-500 bg-emerald-50 shadow-sm"
                              : "border-gray-200 bg-white hover:border-emerald-300 hover:bg-gray-50"
                          )}
                        >
                          <span className={cn(
                            "text-xs font-medium",
                            isSelected ? "text-emerald-600" : "text-gray-500"
                          )}>
                            {formatDateDisplay(dateData.date, dateData.date_display).split(",")[0]}
                          </span>
                          <span className={cn(
                            "mt-1 text-lg font-bold",
                            isSelected ? "text-emerald-700" : "text-gray-900"
                          )}>
                            {new Date(dateData.date).getDate()}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Time Selection */}
                {selectedDateData && (
                  <div>
                    <label className="mb-3 block text-sm font-medium text-gray-700">
                      {t("selectTime")}
                    </label>
                    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
                      {selectedDateData.slots.map((slot) => {
                        const isSelected = selectedTime === slot.datetime;
                        return (
                          <button
                            key={slot.datetime}
                            type="button"
                            onClick={() => handleTimeSelect(slot)}
                            className={cn(
                              "relative rounded-xl border-2 px-3 py-3 text-sm font-medium transition-all",
                              isSelected
                                ? "border-emerald-500 bg-emerald-50 text-emerald-700 shadow-sm"
                                : "border-gray-200 bg-white text-gray-700 hover:border-emerald-300 hover:bg-gray-50"
                            )}
                          >
                            {isRTL ? slot.display_ar : slot.display}
                            {isSelected && (
                              <div className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500">
                                <Check className="h-3 w-3 text-white" />
                              </div>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Selected Time Display */}
                {selectedTime && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 rounded-xl bg-emerald-50 p-4"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500">
                      <Check className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-emerald-800">
                        {t("scheduled")}
                      </p>
                      <p className="text-sm text-emerald-600">
                        {formatDateDisplay(selectedDate!, "")} -{" "}
                        {selectedDateData?.slots.find((s) => s.datetime === selectedTime)?.[
                          isRTL ? "display_ar" : "display"
                        ]}
                      </p>
                    </div>
                  </motion.div>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
