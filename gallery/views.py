from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import MediaCategory, Media, MediaComment, MediaLike
from weddings.models import Wedding

@login_required
def gallery_list(request):
    """List all media the user has access to"""
    user = request.user
    wedding_id = request.GET.get('wedding')

    # Filter by wedding if provided
    if wedding_id:
        wedding = get_object_or_404(Wedding, id=wedding_id)

        # Check if user has access to this wedding
        if user.profile.role == 'admin' and wedding.admin != user:
            return HttpResponseForbidden("You don't have permission to view gallery for this wedding.")

        if user.profile.role == 'team_member' and not wedding.team_members.filter(member=user).exists():
            return HttpResponseForbidden("You don't have permission to view gallery for this wedding.")

        if user.profile.role == 'guest' and not user.guest_profiles.filter(wedding=wedding).exists():
            return HttpResponseForbidden("You don't have permission to view gallery for this wedding.")

        # Get media for this wedding
        media_items = Media.objects.filter(wedding=wedding, is_private=False).order_by('-upload_date')

        # If admin or team member, also show private media
        if user.profile.role in ['admin', 'team_member']:
            private_media = Media.objects.filter(wedding=wedding, is_private=True).order_by('-upload_date')
            media_items = list(media_items) + list(private_media)

        # Get categories for this wedding
        categories = MediaCategory.objects.filter(wedding=wedding)

        context = {
            'media_items': media_items,
            'categories': categories,
            'wedding': wedding
        }
    else:
        # Show all media based on user role
        if user.profile.role == 'admin':
            # Admin sees media for weddings they administer
            admin_weddings = Wedding.objects.filter(admin=user)
            media_items = Media.objects.filter(wedding__in=admin_weddings).order_by('wedding', '-upload_date')
        elif user.profile.role == 'team_member':
            # Team member sees media for weddings they're assigned to
            weddings = [team.wedding for team in user.wedding_teams.all()]
            media_items = Media.objects.filter(wedding__in=weddings).order_by('wedding', '-upload_date')
        else:
            # Guest sees media for weddings they're invited to
            guest_profiles = user.guest_profiles.all()
            weddings = [guest.wedding for guest in guest_profiles]
            media_items = Media.objects.filter(wedding__in=weddings, is_private=False).order_by('wedding', '-upload_date')

        context = {'media_items': media_items}

    return render(request, 'gallery/gallery_list.html', context)

@login_required
def media_detail(request, media_id):
    """View media details"""
    media = get_object_or_404(Media, id=media_id)

    # Check if user has access to this media
    user = request.user
    has_access = False

    if user.profile.role == 'admin' and media.wedding.admin == user:
        has_access = True
    elif user.profile.role == 'team_member' and media.wedding.team_members.filter(member=user).exists():
        has_access = True
    elif user.profile.role == 'guest' and user.guest_profiles.filter(wedding=media.wedding).exists():
        if not media.is_private:
            has_access = True

    if not has_access:
        return HttpResponseForbidden("You don't have permission to view this media.")

    # Get comments
    comments = media.comments.all().order_by('created_at')

    # Check if user has liked this media
    user_liked = media.likes.filter(user=user).exists()

    # Handle comment submission
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'comment':
            comment_text = request.POST.get('comment')

            if comment_text:
                MediaComment.objects.create(
                    media=media,
                    user=user,
                    comment=comment_text
                )

                messages.success(request, "Comment added successfully.")

        elif action == 'like':
            # Toggle like status
            if user_liked:
                media.likes.filter(user=user).delete()
                messages.success(request, "You unliked this media.")
                user_liked = False
            else:
                MediaLike.objects.create(
                    media=media,
                    user=user
                )
                messages.success(request, "You liked this media.")
                user_liked = True

        return redirect('media_detail', media_id=media.id)

    context = {
        'media': media,
        'comments': comments,
        'user_liked': user_liked,
    }

    return render(request, 'gallery/media_detail.html', context)

@login_required
def gallery_upload(request):
    """Upload media to gallery"""
    # Only admins, team members, and guests can upload media
    if request.user.profile.role not in ['admin', 'team_member', 'guest']:
        messages.error(request, "You don't have permission to upload media.")
        return redirect('dashboard')

    # Get wedding if provided in query params
    wedding_id = request.GET.get('wedding')
    if wedding_id:
        wedding = get_object_or_404(Wedding, id=wedding_id)

        # Check if user has access to this wedding
        if request.user.profile.role == 'admin' and wedding.admin != request.user:
            return HttpResponseForbidden("You don't have permission to upload media to this wedding.")

        if request.user.profile.role == 'team_member' and not wedding.team_members.filter(member=request.user).exists():
            return HttpResponseForbidden("You don't have permission to upload media to this wedding.")

        if request.user.profile.role == 'guest' and not request.user.guest_profiles.filter(wedding=wedding).exists():
            return HttpResponseForbidden("You don't have permission to upload media to this wedding.")
    else:
        wedding = None

    if request.method == 'POST':
        # Process form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        wedding_id = request.POST.get('wedding')
        category_id = request.POST.get('category')
        media_type = request.POST.get('media_type')
        is_private = request.POST.get('is_private') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'

        if not title or not wedding_id or not media_type or 'file' not in request.FILES:
            messages.error(request, "Title, wedding, media type, and file are required fields.")
            return redirect('gallery_upload')

        wedding = get_object_or_404(Wedding, id=wedding_id)
        file = request.FILES['file']

        # Create media
        media = Media.objects.create(
            wedding=wedding,
            title=title,
            description=description,
            media_type=media_type,
            file=file,
            uploaded_by=request.user,
            is_private=is_private,
            is_featured=is_featured
        )

        # Set category if provided
        if category_id:
            media.category_id = category_id
            media.save()

        messages.success(request, f"Media '{title}' uploaded successfully.")
        return redirect('media_detail', media_id=media.id)

    # Get available weddings based on user role
    if request.user.profile.role == 'admin':
        available_weddings = Wedding.objects.filter(admin=request.user)
    elif request.user.profile.role == 'team_member':
        wedding_teams = request.user.wedding_teams.all()
        available_weddings = [team.wedding for team in wedding_teams]
    else:
        guest_profiles = request.user.guest_profiles.all()
        available_weddings = [guest.wedding for guest in guest_profiles]

    # Get categories for the selected wedding
    categories = []
    if wedding:
        categories = MediaCategory.objects.filter(wedding=wedding)

    context = {
        'available_weddings': available_weddings,
        'selected_wedding': wedding,
        'categories': categories,
    }

    return render(request, 'gallery/gallery_upload.html', context)

@login_required
def media_delete(request, media_id):
    """Delete media"""
    media = get_object_or_404(Media, id=media_id)

    # Check if user has permission
    if request.user.profile.role == 'admin' and media.wedding.admin != request.user:
        return HttpResponseForbidden("You don't have permission to delete this media.")

    if request.user.profile.role == 'team_member' and not media.wedding.team_members.filter(member=request.user).exists():
        return HttpResponseForbidden("You don't have permission to delete this media.")

    if request.user.profile.role == 'guest' and request.user != media.uploaded_by:
        return HttpResponseForbidden("You don't have permission to delete this media.")

    if request.method == 'POST':
        wedding = media.wedding
        media_title = media.title
        media.delete()

        messages.success(request, f"Media '{media_title}' deleted successfully.")
        return redirect('gallery_list')

    context = {
        'media': media,
    }

    return render(request, 'gallery/media_confirm_delete.html', context)

@login_required
def wedding_gallery(request, wedding_id):
    """View gallery for a specific wedding"""
    wedding = get_object_or_404(Wedding, id=wedding_id)

    # Check if user has access to this wedding
    user = request.user
    has_access = False

    if user.profile.role == 'admin' and wedding.admin == user:
        has_access = True
    elif user.profile.role == 'team_member' and wedding.team_members.filter(member=user).exists():
        has_access = True
    elif user.profile.role == 'guest' and user.guest_profiles.filter(wedding=wedding).exists():
        has_access = True

    if not has_access:
        return HttpResponseForbidden("You don't have permission to view gallery for this wedding.")

    # Get media for this wedding
    media_items = Media.objects.filter(wedding=wedding, is_private=False).order_by('-upload_date')

    # If admin or team member, also show private media
    if user.profile.role in ['admin', 'team_member']:
        private_media = Media.objects.filter(wedding=wedding, is_private=True).order_by('-upload_date')
        media_items = list(media_items) + list(private_media)

    # Get categories for this wedding
    categories = MediaCategory.objects.filter(wedding=wedding)

    context = {
        'media_items': media_items,
        'categories': categories,
        'wedding': wedding
    }

    return render(request, 'gallery/wedding_gallery.html', context)
