%global         __provides_exclude_from ^/opt/%{name}/.*$
%global         __requires_exclude_from ^/opt/%{name}/.*$
%global         app_name Figma-Linux
%global         debug_package %nil

Name:           %(echo %app_name | tr '[:upper:]' '[:lower:]')
Version:        0.11.5
Release:        1%{?dist}
Summary:        %{app_name} is an unofficial Electron-based Figma desktop app for Linux.

License:        GPL-2.0
URL:            https://github.com/%{app_name}/%{name}

Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

Patch0:         config_builder.json_diff.patch

%ifarch %arm64
BuildRequires:  python3 gcc gcc-c++ make cmake libtool
%endif

BuildRequires:  nodejs nodejs-npm

%description
%summary


%prep
%autosetup -p1 -n ./%{name}-%{version}


%build
# Change the node cache dir to avoid errors in COPR's cloud environment
mkdir -v ./.node_cache
export npm_config_cache="$(readlink -f ./.node_cache)"

# Install the dependencies
env NODE_ENV='dev' npm install

# Generate important build files
export NODE_ENV='production'
npm run build

# Build the application
npm run builder


%install
# Setup buildroot
install -d %{buildroot}{/opt/%{name},%{_bindir},%{_datadir}/applications}

sizes=(
  '24x24' '36x36' '48x48' '64x64' '72x72' '96x96'
  '128x128' '192x192' '256x256' '384x384' '512x512'
)
for size in "${sizes[@]}"; do
  install -d "%{buildroot}%{_iconsdir}/hicolor/$size/apps"
done
install -d %{buildroot}%{_iconsdir}/hicolor/scalable/apps

# Reusable constant
BUILD_DIR=./build/installers/linux-unpacked

# Remove unneeded files in the build directory
rm -r "$BUILD_DIR"/{usr,lib,AppRun} "$BUILD_DIR"/*.sh

# Copy the application files to the application directory
cp -a "$BUILD_DIR"/* %{buildroot}/opt/%{name}

# Install the desktop file
install -Dm 0644 ./resources/%{name}.desktop -t %{buildroot}%{_datadir}/applications

# Create a symlink to the application binary
ln -s /opt/%{name}/%{name} %{buildroot}%{_bindir}

# Install application icons
for size in "${sizes[@]}"; do
  install -Dm 0644 "$BUILD_DIR/icons/$size.png" \
    "%{buildroot}%{_iconsdir}/hicolor/$size/apps/%{name}.png"
done
install -Dm 0644 "$BUILD_DIR/icons/scalable.svg" \
  %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.png

# Remove unneeded files in the application directory
rm -r %{buildroot}/opt/%{name}/icons


%files
/opt/%{name}
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png

%changelog
%autochangelog
