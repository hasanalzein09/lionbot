"use client";

import { useState, useEffect } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Clock, Calendar, Loader2 } from "lucide-react";
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
          setError(locale === "ar" ? "فشل في تحميل الأوقات" : "Failed to load time slots");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [isScheduled, restaurantId, locale]);

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
      return locale === "ar" ? "اليوم" : "Today";
    }
    if (date.toDateString() === tomorrow.toDateString()) {
      return locale === "ar" ? "غداً" : "Tomorrow";
    }

    // Format as day name in Arabic
    if (locale === "ar") {
      const days = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"];
      return days[date.getDay()];
    }

    return displayStr;
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Clock className="h-5 w-5 text-primary-500" />
        <h3 className="font-semibold">{t("title")}</h3>
      </div>

      {/* ASAP vs Schedule Toggle */}
      <div className="flex gap-3">
        <Button
          type="button"
          variant={!isScheduled ? "default" : "outline"}
          className={cn(
            "flex-1 transition-all",
            !isScheduled && "ring-2 ring-primary-500 ring-offset-2 ring-offset-background"
          )}
          onClick={handleAsapClick}
        >
          <span className="mr-2">⚡</span>
          {t("asap")}
        </Button>
        <Button
          type="button"
          variant={isScheduled ? "default" : "outline"}
          className={cn(
            "flex-1 transition-all",
            isScheduled && "ring-2 ring-primary-500 ring-offset-2 ring-offset-background"
          )}
          onClick={handleScheduleClick}
        >
          <Calendar className="mr-2 h-4 w-4" />
          {t("schedule")}
        </Button>
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
                <Loader2 className="h-6 w-6 animate-spin text-primary-500" />
              </div>
            ) : error ? (
              <div className="rounded-lg bg-error-500/10 p-3 text-center text-sm text-error-500">
                {error}
              </div>
            ) : (
              <>
                {/* Date Selection */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-muted-foreground">
                    {t("selectDate")}
                  </label>
                  <div className="scrollbar-hide flex gap-2 overflow-x-auto pb-2">
                    {dates.slice(0, 7).map((dateData) => (
                      <button
                        key={dateData.date}
                        type="button"
                        onClick={() => handleDateSelect(dateData.date)}
                        className={cn(
                          "flex min-w-[80px] flex-col items-center rounded-xl border-2 px-3 py-2 transition-all",
                          selectedDate === dateData.date
                            ? "border-primary-500 bg-primary-500/10 text-primary-500"
                            : "border-border hover:border-primary-500/50"
                        )}
                      >
                        <span className="text-xs text-muted-foreground">
                          {formatDateDisplay(dateData.date, dateData.date_display).split(",")[0]}
                        </span>
                        <span className="font-medium">
                          {new Date(dateData.date).getDate()}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Time Selection */}
                {selectedDateData && (
                  <div>
                    <label className="mb-2 block text-sm font-medium text-muted-foreground">
                      {t("selectTime")}
                    </label>
                    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
                      {selectedDateData.slots.map((slot) => (
                        <button
                          key={slot.datetime}
                          type="button"
                          onClick={() => handleTimeSelect(slot)}
                          className={cn(
                            "rounded-lg border-2 px-3 py-2 text-sm transition-all",
                            selectedTime === slot.datetime
                              ? "border-primary-500 bg-primary-500/10 font-medium text-primary-500"
                              : "border-border hover:border-primary-500/50"
                          )}
                        >
                          {locale === "ar" ? slot.display_ar : slot.display}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Selected Time Display */}
                {selectedTime && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="rounded-lg bg-success-500/10 p-3 text-center text-sm text-success-500"
                  >
                    {t("scheduled")}:{" "}
                    <span className="font-medium">
                      {formatDateDisplay(selectedDate!, "")} -{" "}
                      {selectedDateData?.slots.find((s) => s.datetime === selectedTime)?.[
                        locale === "ar" ? "display_ar" : "display"
                      ]}
                    </span>
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
