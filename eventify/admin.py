from django.contrib import admin
from .models import Event, Ticket, Category
from .models import EventStatusEnum

# Инлайн для отображения билетов внутри события
class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ('user', 'booked_at')


# Кастомный фильтр по статусу события из билетов
class EventStatusFilter(admin.SimpleListFilter):
    title = 'Event status'
    parameter_name = 'event__status'

    def lookups(self, request, model_admin):
        return EventStatusEnum.choices()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(event__status=self.value())
        return queryset


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'status')
    list_filter = ('status', 'date')
    search_fields = ('title', 'description', 'location')
    inlines = [TicketInline]
    filter_horizontal = ('categories',)  # Удобный выбор ManyToMany


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'booked_at')
    list_filter = ('event', EventStatusFilter)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('status',)

# Register your models here.
# admin.site.register(Event)
# admin.site.register(Ticket)
# admin.site.register(Category)