# PHP + Apache for SPRS
FROM php:8.2-apache

# Install extensions
RUN docker-php-ext-install pdo pdo_mysql

# Enable Apache modules
RUN a2enmod rewrite

# Set Apache DocumentRoot to /var/www/html/public
ENV APACHE_DOCUMENT_ROOT=/var/www/html/public
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/000-default.conf \
    && sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}/../!g' /etc/apache2/apache2.conf

# Copy app into container
COPY . /var/www/html/

# Permissions (simple, for dev)
RUN chown -R www-data:www-data /var/www/html \
    && find /var/www/html -type f -exec chmod 0644 {} \; \
    && find /var/www/html -type d -exec chmod 0755 {} \;

EXPOSE 80
CMD ["apache2-foreground"]