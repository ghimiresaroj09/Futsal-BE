from django.db import migrations


def create_testimonial_table(apps, schema_editor):
    """Ensure cms_testimonial table exists with correct schema."""
    schema_editor.execute("""
        CREATE TABLE IF NOT EXISTS cms_testimonial (
            id UUID PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
            full_name VARCHAR(200) NOT NULL,
            title VARCHAR(200) NOT NULL,
            image VARCHAR(255),
            content TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            sort_order INTEGER NOT NULL DEFAULT 0
        );
    """)
    schema_editor.execute("""
        CREATE INDEX IF NOT EXISTS cms_testimonial_created_at_idx 
        ON cms_testimonial (created_at);
    """)


def reverse_migration(apps, schema_editor):
    """Do nothing on reverse - we don't want to drop the table."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0011_alter_carouselimage_image_alter_galleryimage_image_and_more'),
    ]

    operations = [
        migrations.RunPython(create_testimonial_table, reverse_migration),
    ]
